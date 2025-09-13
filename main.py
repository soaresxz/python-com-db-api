from fastapi import FastAPI, HTTPException, status, Query
from typing import List, Optional

import database
import repository
import schemas

app = FastAPI(
    title="API da Biblioteca",
    description="API para gerenciar os livros da biblioteca.",
    version="1.0.0"
)

@app.on_event("startup")
def on_startup():
    database.init_db()

@app.post("/livros/", response_model=schemas.Livro, status_code=status.HTTP_201_CREATED, tags=["Livros"])
def criar_livro(livro: schemas.LivroCreate):
    """Cria um novo livro no banco de dados."""
    novo_id = repository.adicionar_livro(
        titulo=livro.titulo,
        autor=livro.autor,
        editora=livro.editora,
        categoria=livro.categoria,
        ano=livro.ano
    )
    livro_criado = repository.buscar_livro_por_id(novo_id)
    return livro_criado

@app.get("/livros/", response_model=List[schemas.Livro], tags=["Livros"])
def listar_todos_os_livros():
    """Retorna uma lista de todos os livros (exceto os removidos logicamente)."""
    return repository.listar_livros()

@app.get("/livros/buscar", response_model=List[schemas.Livro], tags=["Livros"])
def buscar_livros_por_termo(termo: str = Query(..., min_length=3, description="Termo para buscar em títulos, autores ou editoras.")):
    """Busca por livros que contenham o termo no título, autor ou editora."""
    return repository.buscar_livros(termo)


@app.patch("/livros/{livro_id}/disponibilidade", response_model=schemas.Livro, tags=["Livros"])
def atualizar_disponibilidade_livro(livro_id: int, payload: schemas.UpdateDisponibilidade):
    """Atualiza o status de disponibilidade de um livro (disponível/emprestado)."""
    if not repository.buscar_livro_por_id(livro_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Livro não encontrado")

    repository.atu_disp(livro_id, payload.disponivel)
    return repository.buscar_livro_por_id(livro_id)

@app.delete("/livros/{livro_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Livros"])
def remover_livro_logicamente(livro_id: int):
    """Marca um livro como 'removido' (soft delete), mas o mantém no banco de dados."""
    if not repository.deletar_livro_logico(livro_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Livro não encontrado")
    return None

@app.delete("/livros/{livro_id}/permanente", status_code=status.HTTP_204_NO_CONTENT, tags=["Livros"])
def remover_livro_permanentemente(livro_id: int):
    """
    **Atenção:** Remove permanentemente o registro de um livro do banco de dados.
    Esta ação não pode ser desfeita.
    """
    if not repository.deletar_fisico(livro_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Livro não encontrado")
    return None