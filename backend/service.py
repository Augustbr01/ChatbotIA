import aiosqlite
from typing import List, Dict, Any
from datetime import datetime
from llm import enviarMensagemLLM

ORCAMENTO_MAXIMO_CARACTERES = 4000
caminho_db = "backend/database/chatbot.db"

# ========== Funções de Serviço ============

async def get_conversas_db(conn: aiosqlite.Connection) -> List[Dict[str, Any]]:
    # Lista todas as conversas do banco de dados
    cursor = await conn.execute("SELECT conversa_id, titulo, data_criacao FROM conversas ORDER BY conversa_id DESC")
    rows = await cursor.fetchall()
    
    lista_formatada = []
    for row in rows:
        lista_formatada.append({
            "conversa_id": row[0],
            "titulo": row[1],
            "data_criacao": row[2]
        })
    return lista_formatada

async def create_conversa_db(conn: aiosqlite.Connection, titulo: str) -> Dict[str, Any]:
    # Criar nova conversa no banco de dados
    data_atual = datetime.now().isoformat()
    
    cursor = await conn.execute("INSERT INTO conversas (titulo, data_criacao) VALUES (?, ?)", (titulo, data_atual))
    await conn.commit()
    
    id = cursor.lastrowid
    
    return {
        "conversa_id": id,
        "titulo": titulo,
        "data_criacao": data_atual
    }

async def get_mensagens_db(conn: aiosqlite.Connection, conversa_id: int) -> List[Dict[str, Any]]:
    # Lista todas as mensagens de uma conversa especifica
    await conn.execute("PRAGMA foreign_keys = ON;")
    
    cursor = await conn.execute("SELECT mensagem_id, remetente, conteudo, timestamp FROM mensagens WHERE conversa_id = ? ORDER BY timestamp ASC", (conversa_id,))
    rows = await cursor.fetchall()
    
    lista = []
    for row in rows:
        lista.append({
            "mensagem_id": row[0],
            "remetente": row[1],
            "conteudo": row[2],
            "timestamp": row[3]
        })
    return lista

async def send_message_service(conn: aiosqlite.Connection, conversa_id: int, conteudo: str) -> Dict[str, Any]:
    # Processa o envio de uma mensagem, gera a resposta da IA e salva no banco.
    data_atual = datetime.now().isoformat()

    cursor = await conn.execute("SELECT COUNT(*) FROM mensagens WHERE conversa_id = ?", (conversa_id,))
    (qtd,) = await cursor.fetchone()
    if qtd < 1:
        primeiramensagem = True
    else:
        primeiramensagem = False
    
    respostatitulo = None
    
    # 1. Lógica de Geração de Título (Se for a primeira mensagem)
    if primeiramensagem:
        promptSistema = {
            "role": "system",
            "content": "Você é gerador de titulo, onde recebe uma mensagem e voce deve gerar um titulo de um conversa de 1 linha baseado nessa mensagem. Só deve responder o titulo e nada mais."
        }
        titulorecebido = []
        titulorecebido.append({"role": "user", "content": conteudo})
        mensagemfinal = [promptSistema] + titulorecebido
        
        # Chamada assíncrona para o LLM
        respostatituloIA = await enviarMensagemLLM(mensagemfinal)
        respostatitulo = "💬 " + respostatituloIA
        
        # Atualiza o título da conversa
        await conn.execute("UPDATE conversas SET titulo = ? WHERE conversa_id = ?", (respostatitulo, conversa_id))
        await conn.commit()
        
    # 2. Grava a mensagem do usuário
    await conn.execute("INSERT INTO mensagens (conversa_id, remetente, conteudo, timestamp) VALUES (?, ?, ?, ?)", (conversa_id, "Usuario", conteudo, data_atual))
    await conn.commit()
    
    # 3. Extrai o histórico para o LLM
    # Busca o histórico completo (ou um limite alto) e itera de trás para frente
    cursor = await conn.execute("SELECT remetente, conteudo FROM mensagens WHERE conversa_id = ? ORDER BY timestamp DESC LIMIT 20", (conversa_id,))
    historico_invertido = await cursor.fetchall()
    
    mensagens_selecionadas = []
    caracteres_acumulados = 0
    
    promptSistema = {
        "role": "system",
        "content": "Você é um assistente útil. Responda de forma clara e objetiva."
    }
    
    for remetente, conteudo_msg in historico_invertido:
        tamanho_msg = len(conteudo_msg)
        
        if caracteres_acumulados + tamanho_msg > ORCAMENTO_MAXIMO_CARACTERES:
            break
            
        role = "user" if remetente == "Usuario" else "assistant"
        mensagens_selecionadas.append({"role": role, "content": conteudo_msg})
        caracteres_acumulados += tamanho_msg
        
    # Inverte a ordem e adiciona o prompt do sistema
    mensagens_finais = [promptSistema] + mensagens_selecionadas[::-1]
    
    # 4. Gera a resposta da IA
    resposta_ia_texto = await enviarMensagemLLM(mensagens_finais)
    
    data_atual_resposta = datetime.now().isoformat()
    
    # 5. Grava a resposta da IA
    cursor = await conn.execute("INSERT INTO mensagens (conversa_id, remetente, conteudo, timestamp) VALUES (?, ?, ?, ?)", (conversa_id, "IA", resposta_ia_texto, data_atual_resposta))
    await conn.commit()
    
    ia_message_id = cursor.lastrowid
    
    return {
        "mensagem_id": ia_message_id,
        "titulo": respostatitulo,
        "remetente": "IA",
        "conteudo": resposta_ia_texto,
        "timestamp": data_atual_resposta
    }

async def delete_conversa_db(conn: aiosqlite.Connection, conversa_id: int):
   
    await conn.execute("PRAGMA foreign_keys = ON;")    
    await conn.execute("DELETE FROM conversas WHERE conversa_id = ?", (conversa_id,))
    await conn.commit()
    
    return {"Sucesso" : "Conversa excluida"}

