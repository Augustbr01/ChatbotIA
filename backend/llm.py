from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

LOCAL_LLM_URL = os.getenv("LOCAL_LLM_URL", "http://localhost:1234/v1")
LOCAL_LLM_KEY = os.getenv("LOCAL_LLM_KEY", "lm-studio")
LOCAL_LLM_MODEL = os.getenv("LOCAL_LLM_MODEL", "openai/gpt-oss-20b")

REMOTE_LLM_KEY = os.getenv("REMOTE_LLM_KEY", "")
REMOTE_LLM_MODEL = os.getenv("REMOTE_LLM_MODEL", "gpt-4o")

USAR_LLM_LOCAL = os.getenv("USAR_LLM_LOCAL", "True").lower() in ('true', '1', 't')

async def enviarMensagemLLM(mensagens_historico):
    client = None
    modelo = ""

    usar_llm_local = True

    if USAR_LLM_LOCAL:
        client = AsyncOpenAI(
            base_url=LOCAL_LLM_URL,
            api_key=LOCAL_LLM_KEY
        )
        modelo = LOCAL_LLM_MODEL
    else:
        client = AsyncOpenAI(
            api_key= REMOTE_LLM_KEY
        )
        modelo = REMOTE_LLM_MODEL
        
    try:
        response = await client.chat.completions.create(
            model=modelo,
            messages=mensagens_historico,
            temperature=0.7
        )
            
        return response.choices[0].message.content
    except Exception as e:
        print(f"ERRO NO LLM: {e}")
        return f"Erro no envio da LLM: {str(e)}"
    
