import json
import os
import csv
import io
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Depends, Header, HTTPException, status, Form, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlmodel import Session, select, func
from datetime import datetime
from collections import defaultdict
import statistics

load_dotenv()

from .database import create_db_and_tables, get_session
from .models import Gasto, Configuracao
from .services import processar_texto_notificacao, calcular_mes_referencia, get_dia_fechamento, set_dia_fechamento, get_meta_mensal, set_meta_mensal, get_salario, set_salario

app = FastAPI(title="Finance Tracker")
templates = Jinja2Templates(directory="app/templates")

# Função auxiliar para formatar moeda no Template
def formatar_moeda(valor):
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Registra a função no Jinja2 para usar no HTML
templates.env.filters["moeda"] = formatar_moeda

# --- Segurança ---
API_TOKEN = os.getenv("API_TOKEN", "token-padrao-dev")

async def verify_token(x_api_token: str = Header(...)):
    if x_api_token != API_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

class WebhookPayload(BaseModel):
    raw_text: str
    app_name: str
    timestamp: str | None = None

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.post("/webhook", dependencies=[Depends(verify_token)])
async def receber_gasto(payload: WebhookPayload, session: Session = Depends(get_session)):
    print(f"Payload recebido: {payload}")
    
    if "Procurando novas mensagens" in payload.raw_text:
        return {"status": "ignored"}

    dados = processar_texto_notificacao(payload.raw_text)
    print(f"Dados processados: {dados}")
    
    novo_gasto = Gasto(
        valor=dados["valor"],
        estabelecimento=dados["estabelecimento"],
        categoria=dados["categoria"],
        banco=payload.app_name,
        raw_text=payload.raw_text,
        data_compra=datetime.now(),
        mes_referencia=calcular_mes_referencia(session)
    )
    
    session.add(novo_gasto)
    session.commit()
    print(f"Gasto salvo: {novo_gasto.valor}")
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, mes: str = Query(None), session: Session = Depends(get_session)):
    mes_ref_atual = mes or calcular_mes_referencia(session)
    dia_fechamento = get_dia_fechamento(session)
    meta_mensal = get_meta_mensal(session)
    salario = get_salario(session)
    
    # Gastos do mês selecionado
    statement = select(Gasto).where(Gasto.mes_referencia == mes_ref_atual).order_by(Gasto.data_compra.desc())
    gastos = session.exec(statement).all()
    total_mes = sum([g.valor for g in gastos])
    
    # Mês anterior para comparação
    todos_gastos = session.exec(select(Gasto)).all()
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
        "meses_disponiveis": meses_disponiveis
    })

@app.post("/configurar-fatura")
async def configurar_fatura(dia: int = Form(...), session: Session = Depends(get_session)):
    set_dia_fechamento(session, dia)
    return RedirectResponse(url="/", status_code=303)

@app.post("/configurar-meta")
async def configurar_meta(meta: float = Form(...), salario: float = Form(0), session: Session = Depends(get_session)):
    set_meta_mensal(session, meta)
    if salario > 0:
        set_salario(session, salario)
    return RedirectResponse(url="/", status_code=303)

@app.get("/exportar")
async def exportar_csv(mes: str = Query(None), session: Session = Depends(get_session)):
    mes_ref = mes or calcular_mes_referencia(session)
    statement = select(Gasto).where(Gasto.mes_referencia == mes_ref).order_by(Gasto.data_compra.desc())
    gastos = session.exec(statement).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Data", "Estabelecimento", "Categoria", "Valor", "Banco"])
    for g in gastos:
        writer.writerow([g.data_compra.strftime("%d/%m/%Y %H:%M"), g.estabelecimento, g.categoria, g.valor, g.banco])
    
    output.seek(0)
    return StreamingResponse(io.BytesIO(output.getvalue().encode("utf-8")), media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=gastos_{mes_ref}.csv"})