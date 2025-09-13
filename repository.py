import sqlite3
from typing import List, Optional
from enum import Enum
from database import conectar

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

def adicionar_livro(titulo: str, autor: str, editora: str, categoria: Categoria, ano: Optional[int]):
    """Adiciona um novo livro com status ATIVO e DISPONIVEL por padrão."""
    with conectar() as conn:
        cursor = conn.execute(
            """
            INSERT INTO livros (titulo, autor, editora, categoria, ano, disponivel, livro_status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (titulo.strip(), autor.strip(), editora.strip(), categoria.value, ano, 1, Status.ATIVO.value)
        )
        conn.commit()
        return cursor.lastrowid

def listar_livros() -> List[sqlite3.Row]:
    """Lista todos os livros que não foram excluídos (soft delete)."""
    with conectar() as conn:
        cursor = conn.execute(
            "SELECT * FROM livros WHERE livro_status != ?;", (Status.EXCLUIDO.value,)
        )
        return cursor.fetchall()
    
def buscar_livro_por_id(livro_id: int) -> Optional[sqlite3.Row]:
    """Busca um único livro pelo seu ID."""
    with conectar() as conn:
        cursor = conn.execute(
            "SELECT * FROM livros WHERE id = ?;", (livro_id,)
        )
        return cursor.fetchone()

def buscar_livros(termo: str) -> List[sqlite3.Row]:
    """Busca livros por título, autor ou editora."""
    like = f"%{termo.strip()}%"
    with conectar() as conn:
        cursor = conn.execute(
            """
            SELECT * FROM livros
            WHERE (lower(titulo) LIKE lower(?) 
            OR lower(autor) LIKE lower(?) 
            OR lower(editora) LIKE lower(?))
            AND livro_status != ?;
            """,
            (like, like, like, Status.EXCLUIDO.value)
        )
        return cursor.fetchall()

def atu_disp(livro_id: int, disponivel: bool) -> bool:
    """Atualiza o status de disponibilidade de um livro (disponível/emprestado)."""
    with conectar() as conn:
        cursor = conn.execute(
            "UPDATE livros SET disponivel = ? WHERE id = ?",
            (int(disponivel), livro_id)
        )
        conn.commit()
        return cursor.rowcount > 0

def deletar_fisico(livro_id: int) -> bool:
    """Remove permanentemente o registro do livro do banco de dados."""
    with conectar() as conn:
        cursor = conn.execute("DELETE FROM livros WHERE id = ?", (livro_id,))
        conn.commit()
        return cursor.rowcount > 0

def deletar_livro_logico(livro_id: int) -> bool:
    """Realiza um 'soft delete', marcando o livro como excluído."""
    with conectar() as conn:
        cursor = conn.execute(
            "UPDATE livros SET livro_status = ? WHERE id = ?",
            (Status.EXCLUIDO.value, livro_id)
        )
        conn.commit()
        return cursor.rowcount > 0