from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel

class Gasto(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    valor: float
    estabelecimento: str
    categoria: str = "Geral"
    banco: str
    data_compra: datetime = Field(default_factory=datetime.now)
    mes_referencia: str
    raw_text: str

class Configuracao(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    chave: str = Field(unique=True, index=True)
    valor: str