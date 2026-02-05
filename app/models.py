from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel

class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    senha_hash: str
    nome: str
    criado_em: datetime = Field(default_factory=datetime.now)

class Gasto(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id", index=True)
    valor: float
    estabelecimento: str
    categoria: str = "Geral"
    banco: str
    data_compra: datetime = Field(default_factory=datetime.now)
    mes_referencia: str
    raw_text: str

class Configuracao(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id", index=True)
    chave: str = Field(index=True)
    valor: str