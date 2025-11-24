from openai import OpenAI

usar_llm_local = True

def enviarMensagemLLM(mensagens_historico):
    client = None
    modelo = ""

    if usar_llm_local:
        client = OpenAI(
            base_url="https://05c652577638.ngrok-free.app/v1",
            api_key="lm-studio"
        )
        modelo = "openai/gpt-oss-20b"
    else:
        client = OpenAI(
            api_key=""
        )
        modelo = "gpt-4o"

    try:
        response = client.chat.completions.create(
            model=modelo,
            messages=mensagens_historico,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Erro no envio da LLM: {str(e)}"
    
