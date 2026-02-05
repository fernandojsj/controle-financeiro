import re
from datetime import datetime

DIA_FECHAMENTO_FATURA = 25 

def calcular_mes_referencia(data_compra: datetime = None) -> str:
    if not data_compra:
        data_compra = datetime.now()
    
    ano = data_compra.year
    mes = data_compra.month
    
    if data_compra.day >= DIA_FECHAMENTO_FATURA:
        mes += 1
        if mes > 12:
            mes = 1
            ano += 1
            
    return f"{ano}-{mes:02d}"

def categorizar_gasto(estabelecimento: str) -> str:
    est = estabelecimento.lower()
    
    # Regras simples de categorização (pode virar banco de dados depois)
    if any(x in est for x in ["ifood", "restaurante", "padaria", "mercado", "burguer", "pizza"]):
        return "Alimentação"
    if any(x in est for x in ["uber", "99", "posto", "ipiranga", "shell", "estacionamento"]):
        return "Transporte"
    if any(x in est for x in ["netflix", "amazon", "spotify", "steam", "playstation", "xbox"]):
        return "Lazer/Assinaturas"
    if any(x in est for x in ["farmacia", "drogasil", "hospital", "medico"]):
        return "Saúde"
    
    return "Outros"

def processar_texto_notificacao(texto: str):
    # Regex genérico
    padrao = r"(?:R\$|BRL)\s?(?P<valor>[\d,.]+)\s(?:em|no|na)\s(?P<local>.+)"
    match = re.search(padrao, texto, re.IGNORECASE)
    
    if match:
        valor_str = match.group("valor").replace('.', '').replace(',', '.')
        estabelecimento = match.group("local").strip()
        
        return {
            "valor": float(valor_str),
            "estabelecimento": estabelecimento,
            "categoria": categorizar_gasto(estabelecimento), # Nova inteligência
            "sucesso": True
        }
    
    return {
        "valor": 0.0, 
        "estabelecimento": "Não identificado", 
        "categoria": "Erro",
        "sucesso": False
    }