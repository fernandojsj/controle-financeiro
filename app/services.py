import re
import csv
import io
from datetime import datetime
from sqlmodel import Session, select
from typing import List, Dict

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

def get_regras_categorizacao(session: Session, usuario_id: int) -> Dict[str, List[str]]:
    """Retorna regras de categorização do usuário ou padrão expandido"""
    from .models import Configuracao
    config = session.exec(select(Configuracao).where(
        Configuracao.chave == "regras_categorizacao",
        Configuracao.usuario_id == usuario_id
    )).first()
    
    if config:
        import json
        return json.loads(config.valor)
    
    # Regras padrão expandidas e mais precisas
    return {
        "Alimentação": [
            "ifood", "uber eats", "rappi", "restaurante", "padaria", "mercado", "supermercado",
            "burguer", "burger", "pizza", "lanchonete", "cafe", "cafeteria", "bar", "pub",
            "mcdonald", "bk", "subway", "outback", "giraffas", "habib", "china in box",
            "carrefour", "extra", "pão de açucar", "assai", "atacadão", "walmart",
            "hortifruti", "acougue", "açougue", "peixaria", "feira", "quitanda",
            "delivery", "food", "lanches", "sorveteria", "confeitaria", "doceria"
        ],
        "Transporte": [
            "uber", "99", "99pop", "cabify", "taxi", "posto", "ipiranga", "shell", "br",
            "petrobras", "ale", "raizen", "estacionamento", "combustivel", "gasolina",
            "alcool", "álcool", "diesel", "gnv", "pedagio", "pedágio", "zona azul",
            "metrô", "metro", "onibus", "ônibus", "trem", "cptm", "bilhete unico",
            "sem parar", "veloe", "conectcar", "taggy", "oficina", "mecanica",
            "pneu", "lavagem", "troca de oleo", "óleo"
        ],
        "Lazer/Assinaturas": [
            "netflix", "amazon", "prime", "spotify", "deezer", "youtube", "disney",
            "hbo", "max", "paramount", "apple tv", "globoplay", "crunchyroll",
            "steam", "playstation", "xbox", "nintendo", "epic games", "blizzard",
            "cinema", "ingresso", "cinemark", "kinoplex", "shopping", "parque",
            "academia", "smartfit", "bluefit", "gym", "crossfit", "yoga",
            "livro", "livraria", "cultura", "saraiva", "amazon books",
            "show", "teatro", "evento", "ticket", "sympla", "eventim"
        ],
        "Saúde": [
            "farmacia", "farmácia", "drogaria", "drogasil", "pacheco", "são paulo",
            "ultrafarma", "droga raia", "panvel", "pague menos", "venancio",
            "hospital", "clinica", "clínica", "medico", "médico", "consulta",
            "laboratorio", "laboratório", "exame", "raio x", "tomografia",
            "dentista", "odonto", "ortodontia", "psicólogo", "terapeuta",
            "fisioterapia", "quiropraxia", "acupuntura", "nutri", "vacina"
        ],
        "Moradia": [
            "aluguel", "condominio", "condomínio", "iptu", "luz", "energia",
            "agua", "água", "sabesp", "copasa", "caesb", "sanepar",
            "internet", "vivo", "claro", "tim", "oi", "net", "sky",
            "gas", "gás", "ultragaz", "liquigas", "supergasbras",
            "reforma", "construção", "material de construção", "tintas",
            "leroy", "telhanorte", "c&c", "mobilia", "moveis", "móveis"
        ],
        "Educação": [
            "escola", "faculdade", "universidade", "curso", "aula",
            "mensalidade", "matricula", "matrícula", "material escolar",
            "udemy", "coursera", "alura", "rocketseat", "dio",
            "livro didático", "apostila", "caderno", "mochila escolar"
        ],
        "Vestuário": [
            "roupa", "calça", "camisa", "vestido", "sapato", "tenis", "tênis",
            "nike", "adidas", "zara", "renner", "c&a", "riachuelo", "marisa",
            "shein", "shopee fashion", "mercado livre roupa", "calçado",
            "roupa intima", "íntima", "meia", "bone", "boné", "bolsa", "carteira"
        ],
        "Beleza": [
            "salão", "salao", "cabelereiro", "cabeleireiro", "barber", "barbearia",
            "manicure", "pedicure", "depilação", "estética", "estetica",
            "perfume", "maquiagem", "cosmético", "cosmetico", "sephora",
            "shampoo", "condicionador", "creme", "hidratante"
        ]
    }

def aprender_categorizacao(session: Session, usuario_id: int, estabelecimento: str, categoria: str):
    """Aprende com as categorizações manuais do usuário"""
    from .models import Gasto
    
    # Busca gastos similares já categorizados pelo usuário
    est_limpo = estabelecimento.lower().strip()
    gastos_similares = session.exec(
        select(Gasto).where(
            Gasto.usuario_id == usuario_id,
            Gasto.estabelecimento.ilike(f"%{est_limpo}%")
        ).limit(10)
    ).all()
    
    if gastos_similares:
        # Conta as categorias mais usadas para este estabelecimento
        categorias_count = {}
        for g in gastos_similares:
            categorias_count[g.categoria] = categorias_count.get(g.categoria, 0) + 1
        
        # Retorna a categoria mais comum
        if categorias_count:
            return max(categorias_count.items(), key=lambda x: x[1])[0]
    
    return None

def categorizar_gasto(estabelecimento: str, session: Session = None, usuario_id: int = None) -> tuple[str, float]:
    """Retorna (categoria, confiança) onde confiança é 0-1"""
    est = estabelecimento.lower().strip()
    
    # 1. Tenta aprender do histórico do usuário (maior confiança)
    if session and usuario_id:
        categoria_aprendida = aprender_categorizacao(session, usuario_id, estabelecimento, None)
        if categoria_aprendida:
            return (categoria_aprendida, 0.95)
    
    # 2. Usa regras personalizadas do usuário
    if session and usuario_id:
        regras = get_regras_categorizacao(session, usuario_id)
        for categoria, palavras in regras.items():
            for palavra in palavras:
                if palavra in est:
                    # Confiança baseada no tamanho da palavra (palavras maiores = mais específicas)
                    confianca = min(0.9, 0.6 + (len(palavra) / 20))
                    return (categoria, confianca)
    
    # 3. Fallback para regras padrão expandidas
    regras_padrao = get_regras_categorizacao(session, usuario_id) if session and usuario_id else {
        "Alimentação": ["ifood", "restaurante", "padaria", "mercado", "burguer", "pizza", "supermercado"],
        "Transporte": ["uber", "99", "posto", "combustivel", "gasolina", "estacionamento"],
        "Lazer/Assinaturas": ["netflix", "spotify", "cinema", "academia", "steam"],
        "Saúde": ["farmacia", "hospital", "clinica", "medico", "exame"],
        "Moradia": ["aluguel", "luz", "agua", "internet", "gas"],
        "Educação": ["escola", "curso", "faculdade", "livro"],
        "Vestuário": ["roupa", "sapato", "tenis", "loja"],
        "Beleza": ["salao", "barbearia", "perfume", "cosmetico"]
    }
    
    for categoria, palavras in regras_padrao.items():
        for palavra in palavras:
            if palavra in est:
                confianca = min(0.7, 0.4 + (len(palavra) / 20))
                return (categoria, confianca)
    
    # 4. Não identificado - baixa confiança
    return ("Outros", 0.0)

def processar_extrato_csv(conteudo: str, session: Session, usuario_id: int) -> List[Dict]:
    """Processa arquivo CSV de extrato bancário"""
    gastos = []
    
    # Tenta diferentes delimitadores
    for delimiter in [',', ';', '\t']:
        try:
            reader = csv.DictReader(io.StringIO(conteudo), delimiter=delimiter)
            rows = list(reader)
            if len(rows) > 0 and len(rows[0]) > 1:
                break
        except:
            continue
    else:
        return gastos
    
    for row in rows:
        data = None
        valor = None
        descricao = None
        
        # Debug: imprime as colunas encontradas
        print(f"Colunas: {list(row.keys())}")
        print(f"Linha: {row}")
        
        # Mapeia colunas possíveis
        for key in row.keys():
            key_lower = key.lower().strip()
            val = row[key].strip() if row[key] else ''
            
            if not val:
                continue
            
            # Data
            if 'data' in key_lower and not data:
                data = val
            # Valor (prioriza colunas com "valor" ou valores negativos)
            elif any(x in key_lower for x in ['valor', 'value', 'amount', 'total', 'debito', 'débito']) and not valor:
                # Ignora se for crédito/entrada
                if 'credito' not in key_lower and 'crédito' not in key_lower and 'entrada' not in key_lower:
                    valor = val
            # Descrição
            elif any(x in key_lower for x in ['descri', 'estabelecimento', 'description', 'merchant', 'histórico', 'historico']) and not descricao:
                descricao = val
        
        if not all([data, valor, descricao]):
            print(f"Pulando linha - Data: {data}, Valor: {valor}, Descrição: {descricao}")
            continue
        
        # Processa valor
        try:
            # Remove tudo exceto números, vírgula, ponto e sinal negativo
            valor_limpo = re.sub(r'[^\d,.\-]', '', valor)
            
            # Detecta formato brasileiro (1.234,56) vs americano (1,234.56)
            if ',' in valor_limpo and '.' in valor_limpo:
                # Se vírgula vem depois do ponto, é formato brasileiro
                if valor_limpo.rindex(',') > valor_limpo.rindex('.'):
                    valor_limpo = valor_limpo.replace('.', '').replace(',', '.')
                else:
                    valor_limpo = valor_limpo.replace(',', '')
            elif ',' in valor_limpo:
                # Apenas vírgula - assume formato brasileiro se tiver 2 dígitos depois
                partes = valor_limpo.split(',')
                if len(partes[-1]) == 2:
                    valor_limpo = valor_limpo.replace(',', '.')
                else:
                    valor_limpo = valor_limpo.replace(',', '')
            
            valor_float = abs(float(valor_limpo))
            print(f"Valor processado: {valor} -> {valor_limpo} -> {valor_float}")
        except Exception as e:
            print(f"Erro ao processar valor '{valor}': {e}")
            continue
        
        # Processa data
        try:
            data_obj = None
            for fmt in ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y', '%d/%m/%y', '%Y/%m/%d']:
                try:
                    data_obj = datetime.strptime(data.strip(), fmt)
                    break
                except:
                    continue
            
            if not data_obj:
                print(f"Erro ao processar data '{data}'")
                continue
        except Exception as e:
            print(f"Erro ao processar data '{data}': {e}")
            continue
        
        gastos.append({
            'data': data_obj.strftime('%Y-%m-%d'),
            'valor': valor_float,
            'estabelecimento': descricao.strip(),
            'categoria': categorizar_gasto(descricao, session, usuario_id)[0],
            'confianca': categorizar_gasto(descricao, session, usuario_id)[1]
        })
    
    print(f"Total de gastos processados: {len(gastos)}")
    return gastos

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