from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles 
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import os
from database.builddb import create_tables
import sqlite3
from typing import List, Optional
from contextlib import asynccontextmanager
from datetime import date, datetime
from llm import enviarMensagemLLM

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("INFO:    🚀 Inicializando servidor...")
    create_tables()  # executa na inicialização, criando o banco de dados caso nao tenha
    yield # ISSO DIFERENCIA A INICIALIZAÇÃO DO ENCERRAMENTO DO FASTAPI
    print("INFO:    🛑 Encerrando servidor...")

app = FastAPI(lifespan=lifespan)

BASE_DIR = os.path.dirname(__file__)
STATIC_DIR = os.path.join(BASE_DIR, "..", "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# =========================================================================

def get_db_connection():
    conn = sqlite3.connect("backend/database/chatbot.db")
    cursor = conn.cursor()
    return cursor

@app.get("/")
async def root():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))



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
    remetente: str
    conteudo: str
    timestamp: str

class ListarConversa(BaseModel):
    conversas: List[ConversaResponse]

# =======================================================================

# Rotas de Gerenciamento de Conversa

@app.get("/conversas", response_model=List[ConversaResponse])
def get_conversas():
    try:
        conn = sqlite3.connect("backend/database/chatbot.db")
        cursor = conn.cursor()

        cursor.execute("SELECT conversa_id, titulo, data_criacao FROM conversas ORDER BY conversa_id DESC")
        rows = cursor.fetchall()

        conn.close()

        lista_formatada = []

        for row in rows:
            lista_formatada.append({
                "conversa_id": row[0],
                "titulo": row[1],
                "data_criacao": row[2]
            })

        return lista_formatada
    except Exception as e:
        print(f"ERRO NO BANCO (GET Conversas): {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao listar conversas: {str(e)}")
    finally:
        if conn:
            conn.close()

@app.post("/conversas", response_model=ConversaResponse)
def criar_conversa(conversa: ConversaCreate):
    data_atual = datetime.now().isoformat()
    try:
        conn = sqlite3.connect("backend/database/chatbot.db")
        cursor = conn.cursor()

        cursor.execute("INSERT INTO conversas (titulo, data_criacao) VALUES (?, ?)", (conversa.titulo, data_atual))
        conn.commit()

        id = cursor.lastrowid
        conn.close()

        return {
            "conversa_id": id,
            "titulo": conversa.titulo,
            "data_criacao": data_atual
        }
    except Exception as e:
        print(f"ERRO NO BANCO (POST Conversas): {e}")
        # Garante serialização para string
        raise HTTPException(status_code=500, detail=f"Erro ao criar conversa: {str(e)}")
    finally:
        if conn:
            conn.close()

@app.get("/conversas/{conversa_id}/mensagens", response_model=List[MensagemResponse])
def listarMensagens(conversa_id: int):

    try:
        conn = sqlite3.connect("backend/database/chatbot.db")
        cursor = conn.cursor()
        cursor.execute("SELECT mensagem_id, remetente, conteudo, timestamp FROM mensagens WHERE conversa_id = ? ORDER BY timestamp ASC", (conversa_id,))
        rows = cursor.fetchall()

        lista = []

        for row in rows:
            lista.append({
                "mensagem_id": row[0],
                "remetente": row[1],
                "conteudo": row[2],
                "timestamp": row[3]
            })

        return lista
    except Exception as e:
        print(f"ERRO NO BANCO (GET Mensagens): {e}")
        # Garante serialização para string
        raise HTTPException(status_code=500, detail=f"Erro ao criar conversa: {str(e)}")
    finally:
        if conn:
            conn.close()
    
@app.post("/conversas/{conversa_id}/mensagens", response_model=MensagemResponse)
def enviarMensagem(conversa_id: int, mensagem: MensagemCreate):
    data_atual = datetime.now().isoformat()
    conn = None
    try:
        conn = sqlite3.connect("backend/database/chatbot.db")
        cursor = conn.cursor()

        # GRAVANDO NO BANCO DE DADOS
        cursor.execute("INSERT INTO mensagens (conversa_id, remetente, conteudo, timestamp) VALUES (?, ?, ?, ?)", (conversa_id, "Usuario", mensagem.conteudo, data_atual))
        conn.commit()

        user_message_id = cursor.lastrowid

        ORCAMENTO_MAXIMO_CARACTERES = 4000

        # Extraindo historico da conversa do banco de dados
        cursor.execute("SELECT remetente, conteudo FROM mensagens WHERE conversa_id = ? ORDER BY timestamp DESC LIMIT 20", (conversa_id,))
        historico_invertido = cursor.fetchall()

        mensagens_selecionadas = []
        caracteres_acumulados = 0

        promptSistema = {
            "role": "system",
            "content": "Você é um assistente útil. Responda de forma clara e objetiva."
        }

        for remetente, conteudo in historico_invertido:
            tamanho_msg = len(conteudo)

            if caracteres_acumulados + tamanho_msg > ORCAMENTO_MAXIMO_CARACTERES:
                break

            role = "user" if remetente == "Usuario" else "assistant"
            mensagens_selecionadas.append({"role": role, "content": conteudo})
            caracteres_acumulados += tamanho_msg

        ## O ::-1 faz inverter a ordem da lista das mensagens selecionadas
        mensagens_finais = [promptSistema] + mensagens_selecionadas[::-1]

        resposta_ia_texto = enviarMensagemLLM(mensagens_finais)

        data_atual_resposta = datetime.now().isoformat()

        cursor.execute("INSERT INTO mensagens (conversa_id, remetente, conteudo, timestamp) VALUES (?, ?, ?, ?)", (conversa_id, "IA", resposta_ia_texto, data_atual_resposta))
        conn.commit()

        ia_message_id = cursor.lastrowid

        return {
            "mensagem_id": ia_message_id,
            "remetente": "IA",
            "conteudo": resposta_ia_texto,
            "timestamp": data_atual_resposta
        }
    except Exception as e:
        print(f"ERRO NO BANCO (POST Mensagens): {e}")
        # Garante serialização para string
        raise HTTPException(status_code=500, detail=f"Erro ao criar conversa: {str(e)}")
    finally:
        if conn:
            conn.close()




        









        
    


