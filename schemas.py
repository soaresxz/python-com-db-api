from pydantic import BaseModel
from typing import Optional
from enum import Enum

class Categoria(Enum):
    ROMANCE = 1
    ACAO = 2
    FICCAO = 3
    COMEDIA = 4
    SUSPENSE = 5
    TERROR = 6
    OUTROS = 99

class Status(Enum):
    ATIVO = 1
    INATIVO = 2
    EXCLUIDO = 9

class LivroBase(BaseModel):
    titulo: str
    autor: str
    editora: str
    categoria: Categoria
    ano: Optional[int] = None

class LivroCreate(LivroBase):
    pass

class Livro(LivroBase):
    id: int
    disponivel: bool
    livro_status: Status

    class Config:
        from_attributes = True 

class UpdateDisponibilidade(BaseModel):
    disponivel: bool