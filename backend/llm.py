from openai import OpenAI

def enviarMensagemLLM(mensagens_historico):
    client = None
    modelo = ""

    usar_llm_local = True

    if usar_llm_local:
        client = OpenAI(
            base_url="http://localhost:1234/v1",
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
    
