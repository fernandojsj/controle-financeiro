import json
import os
import csv
import io
import bcrypt
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Depends, Header, HTTPException, status, Form, Query, Cookie
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlmodel import Session, select, func
from datetime import datetime
from collections import defaultdict
import statistics
import json

load_dotenv()

from .database import create_db_and_tables, get_session
from .models import Gasto, Configuracao, Usuario
from .services import processar_texto_notificacao, calcular_mes_referencia, get_dia_fechamento, set_dia_fechamento, get_meta_mensal, set_meta_mensal, get_salario, set_salario

app = FastAPI(title="Finance Tracker")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Função auxiliar para formatar moeda no Template
def formatar_moeda(valor):
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Registra a função no Jinja2 para usar no HTML
templates.env.filters["moeda"] = formatar_moeda

# Função para carregar traduções
def get_translations(lang: str = "pt"):
    if lang == "en":
        try:
            with open("app/static/translations_en.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

# Autenticação
async def get_current_user(session_token: str = Cookie(None), session: Session = Depends(get_session)):
    if not session_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Não autenticado")
    
    # Busca usuário pelo email armazenado no cookie (simplificado)
    usuario = session.exec(select(Usuario).where(Usuario.email == session_token)).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário inválido")
    return usuario

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str = Query(None)):
    return templates.TemplateResponse("login.html", {"request": request, "error": error})

@app.post("/login")
async def login(email: str = Form(...), senha: str = Form(...), session: Session = Depends(get_session)):
    usuario = session.exec(select(Usuario).where(Usuario.email == email)).first()
    if not usuario or not bcrypt.checkpw(senha.encode(), usuario.senha_hash.encode()):
        return RedirectResponse(url="/login?error=Email ou senha inválidos", status_code=303)
    
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="session_token", value=email, httponly=True, max_age=86400*30)
    return response

@app.get("/registro", response_class=HTMLResponse)
async def registro_page(request: Request, error: str = Query(None)):
    return templates.TemplateResponse("registro.html", {"request": request, "error": error})

@app.post("/registro")
async def registro(nome: str = Form(...), email: str = Form(...), senha: str = Form(...), session: Session = Depends(get_session)):
    if session.exec(select(Usuario).where(Usuario.email == email)).first():
        return RedirectResponse(url="/registro?error=Email já cadastrado", status_code=303)
    
    senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()
    novo_usuario = Usuario(email=email, senha_hash=senha_hash, nome=nome)
    session.add(novo_usuario)
    session.commit()
    
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="session_token", value=email, httponly=True, max_age=86400*30)
    return response

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("session_token")
    return response

@app.get("/set-language/{lang}")
async def set_language(lang: str, request: Request, mes: str = Query(None)):
    # Preserva o parâmetro mes na URL
    redirect_url = f"/?mes={mes}" if mes else "/"
    response = RedirectResponse(url=redirect_url, status_code=303)
    response.set_cookie(key="lang", value=lang, max_age=86400*365, httponly=False)
    return response

class WebhookPayload(BaseModel):
    raw_text: str
    app_name: str
    user_email: str
    timestamp: str | None = None

async def verify_token(x_token: str = Header(None)):
    expected_token = os.getenv("WEBHOOK_TOKEN", "")
    if not expected_token or x_token != expected_token:
        raise HTTPException(status_code=403, detail="Token inválido")

@app.get("/sw.js")
async def service_worker():
    with open("app/templates/sw.js", "r") as f:
        content = f.read()
    return Response(content=content, media_type="application/javascript")

@app.get("/manifest.json")
async def manifest():
    with open("app/static/manifest.json", "r") as f:
        content = f.read()
    return Response(content=content, media_type="application/json")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.post("/webhook", dependencies=[Depends(verify_token)])
async def receber_gasto(payload: WebhookPayload, session: Session = Depends(get_session)):
    print(f"Payload recebido: {payload}")
    
    if "Procurando novas mensagens" in payload.raw_text:
        return {"status": "ignored"}
    
    # Busca usuário pelo email
    usuario = session.exec(select(Usuario).where(Usuario.email == payload.user_email)).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    dados = processar_texto_notificacao(payload.raw_text)
    print(f"Dados processados: {dados}")
    
    novo_gasto = Gasto(
        usuario_id=usuario.id,
        valor=dados["valor"],
        estabelecimento=dados["estabelecimento"],
        categoria=dados["categoria"],
        banco=payload.app_name,
        raw_text=payload.raw_text,
        data_compra=datetime.now(),
        mes_referencia=calcular_mes_referencia(session, usuario.id)
    )
    
    session.add(novo_gasto)
    session.commit()
    print(f"Gasto salvo: {novo_gasto.valor}")
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, mes: str = Query(None), lang: str = Cookie(None), session_token: str = Cookie(None), session: Session = Depends(get_session)):
    # Redireciona para login se não autenticado
    if not session_token:
        return RedirectResponse(url="/login", status_code=303)
    
    usuario = session.exec(select(Usuario).where(Usuario.email == session_token)).first()
    if not usuario:
        return RedirectResponse(url="/login", status_code=303)
    
    # Define idioma padrão se não existir
    current_lang = lang if lang in ["pt", "en"] else "pt"
    
    # Carrega traduções
    translations = get_translations(current_lang)
    
    mes_ref_atual = mes or calcular_mes_referencia(session, usuario.id)
    dia_fechamento = get_dia_fechamento(session, usuario.id)
    meta_mensal = get_meta_mensal(session, usuario.id)
    salario = get_salario(session, usuario.id)
    
    # Gastos do mês selecionado
    statement = select(Gasto).where(Gasto.mes_referencia == mes_ref_atual, Gasto.usuario_id == usuario.id).order_by(Gasto.data_compra.desc())
    gastos = session.exec(statement).all()
    total_mes = sum([g.valor for g in gastos])
    
    # Mês anterior para comparação
    todos_gastos = session.exec(select(Gasto).where(Gasto.usuario_id == usuario.id)).all()
    gastos_por_mes = defaultdict(float)
    for g in todos_gastos:
        gastos_por_mes[g.mes_referencia] += g.valor
    
    meses_ordenados = sorted(gastos_por_mes.keys())
    idx_atual = meses_ordenados.index(mes_ref_atual) if mes_ref_atual in meses_ordenados else -1
    total_mes_anterior = gastos_por_mes[meses_ordenados[idx_atual-1]] if idx_atual > 0 else 0
    variacao = ((total_mes - total_mes_anterior) / total_mes_anterior * 100) if total_mes_anterior > 0 else 0
    
    # Evolução últimos 12 meses
    evolucao_labels = meses_ordenados[-12:]
    evolucao_valores = [gastos_por_mes[m] for m in evolucao_labels]
    
    # Previsão (média dos últimos 3 meses)
    previsao = statistics.mean(evolucao_valores[-3:]) if len(evolucao_valores) >= 3 else total_mes
    
    # Agrupamento por categoria
    dados_categoria = defaultdict(lambda: {"total": 0, "quantidade": 0})
    for g in gastos:
        dados_categoria[g.categoria]["total"] += g.valor
        dados_categoria[g.categoria]["quantidade"] += 1
    
    categorias_ordenadas = sorted(dados_categoria.items(), key=lambda x: x[1]["total"], reverse=True)
    
    # Top 5 maiores gastos
    top5_gastos = sorted(gastos, key=lambda x: x.valor, reverse=True)[:5]
    
    # Gráfico pizza
    labels = [cat for cat, _ in categorias_ordenadas]
    series = [dados["total"] for _, dados in categorias_ordenadas]
    
    # Lista de meses disponíveis
    meses_disponiveis = sorted(set([g.mes_referencia for g in todos_gastos]), reverse=True)
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "gastos": gastos,
        "total_mes": total_mes,
        "mes_ref": mes_ref_atual,
        "mes_atual": calcular_mes_referencia(session, usuario.id),
        "dia_fechamento": dia_fechamento,
        "meta_mensal": meta_mensal,
        "salario": salario,
        "categorias": categorias_ordenadas,
        "chart_labels_json": json.dumps(labels),
        "chart_data_json": json.dumps(series),
        "evolucao_labels_json": json.dumps(evolucao_labels),
        "evolucao_valores_json": json.dumps(evolucao_valores),
        "previsao": previsao,
        "variacao": variacao,
        "total_mes_anterior": total_mes_anterior,
        "top5_gastos": top5_gastos,
        "meses_disponiveis": meses_disponiveis,
        "lang": current_lang,
        "t": translations
    })

@app.post("/adicionar-gasto")
async def adicionar_gasto(valor: float = Form(...), estabelecimento: str = Form(...), categoria: str = Form(...), banco: str = Form(...), data_gasto: str = Form(...), session: Session = Depends(get_session), usuario: Usuario = Depends(get_current_user)):
    # Converte a data string para datetime
    data_compra = datetime.strptime(data_gasto, "%Y-%m-%d")
    
    # Calcula o mês de referência baseado na data do gasto
    dia_fechamento = get_dia_fechamento(session, usuario.id)
    if data_compra.day >= dia_fechamento:
        mes_referencia = f"{data_compra.year}-{data_compra.month:02d}"
    else:
        if data_compra.month == 1:
            mes_referencia = f"{data_compra.year - 1}-12"
        else:
            mes_referencia = f"{data_compra.year}-{data_compra.month - 1:02d}"
    
    novo_gasto = Gasto(
        usuario_id=usuario.id,
        valor=valor,
        estabelecimento=estabelecimento,
        categoria=categoria,
        banco=banco,
        raw_text=f"Gasto manual: {estabelecimento}",
        data_compra=data_compra,
        mes_referencia=mes_referencia
    )
    session.add(novo_gasto)
    session.commit()
    return RedirectResponse(url="/", status_code=303)

@app.post("/configurar-fatura")
async def configurar_fatura(dia: int = Form(...), session: Session = Depends(get_session), usuario: Usuario = Depends(get_current_user)):
    set_dia_fechamento(session, dia, usuario.id)
    return RedirectResponse(url="/", status_code=303)

@app.post("/configurar-meta")
async def configurar_meta(meta: float = Form(...), salario: float = Form(0), session: Session = Depends(get_session), usuario: Usuario = Depends(get_current_user)):
    set_meta_mensal(session, meta, usuario.id)
    if salario > 0:
        set_salario(session, salario, usuario.id)
    return RedirectResponse(url="/", status_code=303)

@app.post("/editar-gasto")
async def editar_gasto(gasto_id: int = Form(...), valor: float = Form(...), estabelecimento: str = Form(...), categoria: str = Form(...), data_gasto: str = Form(...), session: Session = Depends(get_session), usuario: Usuario = Depends(get_current_user)):
    # Busca o gasto
    gasto = session.exec(select(Gasto).where(Gasto.id == gasto_id, Gasto.usuario_id == usuario.id)).first()
    if not gasto:
        raise HTTPException(status_code=404, detail="Gasto não encontrado")
    
    # Converte a data string para datetime
    data_compra = datetime.strptime(data_gasto, "%Y-%m-%d")
    
    # Calcula o mês de referência baseado na data do gasto
    dia_fechamento = get_dia_fechamento(session, usuario.id)
    if data_compra.day >= dia_fechamento:
        mes_referencia = f"{data_compra.year}-{data_compra.month:02d}"
    else:
        if data_compra.month == 1:
            mes_referencia = f"{data_compra.year - 1}-12"
        else:
            mes_referencia = f"{data_compra.year}-{data_compra.month - 1:02d}"
    
    # Atualiza o gasto
    gasto.valor = valor
    gasto.estabelecimento = estabelecimento
    gasto.categoria = categoria
    gasto.data_compra = data_compra
    gasto.mes_referencia = mes_referencia
    
    session.commit()
    return RedirectResponse(url="/", status_code=303)

@app.post("/excluir-gasto")
async def excluir_gasto(gasto_id: int = Form(...), session: Session = Depends(get_session), usuario: Usuario = Depends(get_current_user)):
    # Busca o gasto
    gasto = session.exec(select(Gasto).where(Gasto.id == gasto_id, Gasto.usuario_id == usuario.id)).first()
    if not gasto:
        raise HTTPException(status_code=404, detail="Gasto não encontrado")
    
    # Exclui o gasto
    session.delete(gasto)
    session.commit()
    return {"status": "ok"}

@app.get("/exportar")
async def exportar_csv(mes: str = Query(None), session: Session = Depends(get_session), usuario: Usuario = Depends(get_current_user)):
    mes_ref = mes or calcular_mes_referencia(session, usuario.id)
    statement = select(Gasto).where(Gasto.mes_referencia == mes_ref, Gasto.usuario_id == usuario.id).order_by(Gasto.data_compra.desc())
    gastos = session.exec(statement).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Data", "Estabelecimento", "Categoria", "Valor", "Banco"])
    for g in gastos:
        writer.writerow([g.data_compra.strftime("%d/%m/%Y %H:%M"), g.estabelecimento, g.categoria, g.valor, g.banco])
    
    output.seek(0)
    return StreamingResponse(io.BytesIO(output.getvalue().encode("utf-8")), media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=gastos_{mes_ref}.csv"})