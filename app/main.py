import json
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Depends, Header, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlmodel import Session, select
from datetime import datetime

load_dotenv()  # Carrega variáveis do .env

from .database import create_db_and_tables, get_session
from .models import Gasto
from .services import processar_texto_notificacao, calcular_mes_referencia, DIA_FECHAMENTO_FATURA

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
        mes_referencia=calcular_mes_referencia()
    )
    
    session.add(novo_gasto)
    session.commit()
    print(f"Gasto salvo: {novo_gasto.valor}")
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, session: Session = Depends(get_session)):
    mes_ref_atual = calcular_mes_referencia()
    
    statement = select(Gasto).where(Gasto.mes_referencia == mes_ref_atual).order_by(Gasto.data_compra.desc())
    gastos = session.exec(statement).all()
    
    total_mes = sum([g.valor for g in gastos])
    
    # --- Agrupamento para o Gráfico ---
    dados_grafico = {}
    for g in gastos:
        cat = g.categoria
        if cat in dados_grafico:
            dados_grafico[cat] += g.valor
        else:
            dados_grafico[cat] = g.valor
            
    labels = list(dados_grafico.keys())
    series = list(dados_grafico.values())
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "gastos": gastos,
        "total_mes": total_mes,
        "mes_ref": mes_ref_atual,
        "dia_fechamento": DIA_FECHAMENTO_FATURA,
        # Convertendo para string JSON aqui no Python para evitar erros no HTML
        "chart_labels_json": json.dumps(labels),
        "chart_data_json": json.dumps(series)
    })