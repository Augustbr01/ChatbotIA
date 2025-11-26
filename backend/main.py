from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles 
from fastapi.responses import FileResponse
import os
from database.builddb import initialize_db
import aiosqlite
from typing import List
from contextlib import asynccontextmanager
from datetime import datetime
from llm import enviarMensagemLLM
from database.database import get_db
from service import (
    get_conversas_db,
    create_conversa_db,
    get_mensagens_db,
    send_message_service,
    delete_conversa_db
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("INFO:    🚀 Inicializando servidor...")
    await initialize_db()  # executa na inicialização, criando o banco de dados caso nao tenha
    yield # ISSO DIFERENCIA A INICIALIZAÇÃO DO ENCERRAMENTO DO FASTAPI
    print("INFO:    🛑 Encerrando servidor...")

app = FastAPI(lifespan=lifespan)

BASE_DIR = os.path.dirname(__file__)
STATIC_DIR = os.path.join(BASE_DIR, "..", "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# =========================================================================

@app.get("/")
async def root():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.get("/chat")
def rootChat():
    return FileResponse(os.path.join(STATIC_DIR, "chat.html"))


# ========================== Modelos pydantic =============================

class ConversaCreate(BaseModel):
    titulo: str

class ConversaResponse(BaseModel):
    conversa_id: int
    titulo: str
    data_criacao: str

class MensagemCreate(BaseModel):
    conteudo: str

class MensagemResponse(BaseModel):
    mensagem_id: int
    titulo: str | None = None
    remetente: str
    conteudo: str
    timestamp: str

class ListarConversa(BaseModel):
    conversas: List[ConversaResponse]

# =======================================================================

# Rotas de Gerenciamento de Conversa

@app.get("/conversas", response_model=List[ConversaResponse])
async def get_conversas(conn: aiosqlite.Connection = Depends(get_db)):
    try:
        return await get_conversas_db(conn)
    except Exception as e:
        print(f"ERRO NO BANCO (GET Conversas): {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao listar conversas: {str(e)}")


@app.post("/conversas", response_model=ConversaResponse)
async def criar_conversa(conversa: ConversaCreate, conn: aiosqlite.Connection = Depends(get_db)):
    try:
        return await create_conversa_db(conn, conversa.titulo)
    except Exception as e:
        print(f"ERRO NO BANCO (POST Conversas): {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao criar conversa: {str(e)}")

@app.get("/conversas/{conversa_id}/mensagens", response_model=List[MensagemResponse])
async def listarMensagens(conversa_id: int, conn: aiosqlite.Connection = Depends(get_db)):
    try:
        return await get_mensagens_db(conn, conversa_id)
    except Exception as e:
        print(f"ERRO NO BANCO (GET Mensagens): {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao listar mensagens: {str(e)}")
    
@app.post("/conversas/{conversa_id}/mensagens", response_model=MensagemResponse)
async def enviarMensagem(conversa_id: int, mensagem: MensagemCreate, conn: aiosqlite.Connection = Depends(get_db)):
    try:
        return await send_message_service(conn, conversa_id, mensagem.conteudo)
    except Exception as e:
        print(f"ERRO NO BANCO (POST Mensagens): {e}")
        # Garante serialização para string
        raise HTTPException(status_code=500, detail=f"Erro ao criar conversa: {str(e)}")


@app.delete("/conversas/{conversa_id}")
async def excluirConversas(conversa_id: int, conn: aiosqlite.Connection = Depends(get_db)):
    try:
        return await delete_conversa_db(conn, conversa_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao excluir conversa: {str(e)}")

        
@app.delete("/api/db")
async def clearDB():
    caminhoDB = "backend/database/chatbot.db"
    if os.path.exists(caminhoDB):
        os.remove(caminhoDB)
    await initialize_db()
    return { "Sucesso": "Banco de dados resetado!"}

