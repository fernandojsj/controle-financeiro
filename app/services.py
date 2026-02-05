import re
from datetime import datetime
from sqlmodel import Session, select

DIA_FECHAMENTO_FATURA = 25

def get_dia_fechamento(session: Session, usuario_id: int) -> int:
    from .models import Configuracao
    config = session.exec(select(Configuracao).where(Configuracao.chave == "dia_fechamento", Configuracao.usuario_id == usuario_id)).first()
    return int(config.valor) if config else DIA_FECHAMENTO_FATURA

def set_dia_fechamento(session: Session, dia: int, usuario_id: int):
    from .models import Configuracao
    config = session.exec(select(Configuracao).where(Configuracao.chave == "dia_fechamento", Configuracao.usuario_id == usuario_id)).first()
    if config:
        config.valor = str(dia)
    else:
        config = Configuracao(chave="dia_fechamento", valor=str(dia), usuario_id=usuario_id)
        session.add(config)
    session.commit()

def calcular_mes_referencia(session: Session, usuario_id: int, data_compra: datetime = None) -> str:
    if not data_compra:
        data_compra = datetime.now()
    
    dia_fechamento = get_dia_fechamento(session, usuario_id)
    ano = data_compra.year
    mes = data_compra.month
    
    if data_compra.day >= dia_fechamento:
        mes += 1
        if mes > 12:
            mes = 1
            ano += 1
            
    return f"{ano}-{mes:02d}"

def get_meta_mensal(session: Session, usuario_id: int) -> float:
    from .models import Configuracao
    config = session.exec(select(Configuracao).where(Configuracao.chave == "meta_mensal", Configuracao.usuario_id == usuario_id)).first()
    return float(config.valor) if config else 0.0

def set_meta_mensal(session: Session, meta: float, usuario_id: int):
    from .models import Configuracao
    config = session.exec(select(Configuracao).where(Configuracao.chave == "meta_mensal", Configuracao.usuario_id == usuario_id)).first()
    if config:
        config.valor = str(meta)
    else:
        config = Configuracao(chave="meta_mensal", valor=str(meta), usuario_id=usuario_id)
        session.add(config)
    session.commit()

def get_salario(session: Session, usuario_id: int) -> float:
    from .models import Configuracao
    config = session.exec(select(Configuracao).where(Configuracao.chave == "salario", Configuracao.usuario_id == usuario_id)).first()
    return float(config.valor) if config else 0.0

def set_salario(session: Session, salario: float, usuario_id: int):
    from .models import Configuracao
    config = session.exec(select(Configuracao).where(Configuracao.chave == "salario", Configuracao.usuario_id == usuario_id)).first()
    if config:
        config.valor = str(salario)
    else:
        config = Configuracao(chave="salario", valor=str(salario), usuario_id=usuario_id)
        session.add(config)
    session.commit()

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
    # Múltiplos padrões para diferentes formatos de notificação
    padroes = [
        r"(?:R\$|BRL)\s?([\d,.]+)\s+(?:em|no|na|de)\s+(.+?)(?:\.|$)",
        r"(?:compra|pagamento|transação).*?(?:R\$|BRL)\s?([\d,.]+).*?(?:em|no|na|de)\s+(.+?)(?:\.|$)",
        r"(?:aprovad[oa]).*?(?:R\$|BRL)\s?([\d,.]+).*?(?:em|no|na|de)\s+(.+?)(?:\.|$)",
        r"(?:R\$|BRL)\s?([\d,.]+)\s+-\s+(.+?)(?:\.|$)",
    ]
    
    for padrao in padroes:
        match = re.search(padrao, texto, re.IGNORECASE | re.DOTALL)
        if match:
            valor_str = match.group(1).replace('.', '').replace(',', '.')
            estabelecimento = match.group(2).strip()
            
            # Limpa o estabelecimento
            estabelecimento = re.sub(r'\s+', ' ', estabelecimento)
            estabelecimento = estabelecimento.split('\n')[0].strip()
            
            return {
                "valor": float(valor_str),
                "estabelecimento": estabelecimento,
                "categoria": categorizar_gasto(estabelecimento),
                "sucesso": True
            }
    
    return {
        "valor": 0.0, 
        "estabelecimento": "Não identificado", 
        "categoria": "Erro",
        "sucesso": False
    }