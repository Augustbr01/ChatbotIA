# ChatbotIA

Aplicação de chat que combina um backend FastAPI com persistência em SQLite e uma interface web estática para conversar com um modelo de linguagem (local via LM Studio ou remoto via OpenAI). Este documento detalha a arquitetura, dependências e fluxos de uso/manutenção do projeto.

## Visão Geral

- **Backend (`backend/`)** expõe APIs REST para criar conversas, registrar mensagens e acionar a LLM configurada em `backend/llm.py`.
- **Frontend (`static/`)** é hospedado pelo próprio FastAPI via `StaticFiles` e fornece a experiência de chat single-page (`chat.html`, `chat.js`, `chat.css`).
- **Banco (`backend/database/chatbot.db`)** guarda conversas/mensagens em SQLite, inicializado automaticamente no ciclo de vida do FastAPI (`lifespan` em `backend/main.py`).
- **LLM** pode ser atendida localmente (por padrão) usando LM Studio exposto por ngrok, ou remotamente alterando a flag `usar_llm_local`.

```
Navegador ── HTTP ── FastAPI (`backend/main.py`) ── SQLite
                                 │
                                 └── `enviarMensagemLLM()` → OpenAI API (local/remoto)
```

## Estrutura do Projeto

```
ChatbotIA/
├─ backend/
│  ├─ main.py               # API FastAPI, rotas e ciclo de vida
│  ├─ llm.py                # Cliente OpenAI (local/remoto)
│  └─ database/
│     ├─ builddb.py         # Criação de tabelas
│     └─ chatbot.db         # Banco SQLite (gerado)
├─ static/
│  ├─ index.html            # Landing page com redirecionamento
│  ├─ chat.html             # Interface principal
│  ├─ chat.css              # Estilos
│  └─ chat.js               # Lógica do cliente (fetch/DOM)
└─ venv/                    # Ambiente virtual Python (opcional)
```

## Pré-Requisitos

- Python 3.11+ (o projeto usa `venv`, disponível na pasta `venv/`).
- Pip para instalar dependências (`fastapi`, `openai`, etc.).
- LM Studio (opcional) com endpoint HTTP exposto, caso deseje rodar a LLM localmente.

## Configuração e Execução

1. **Clonar/instalar dependências**
   ```bash
   python -m venv venv
   venv\Scripts\activate            # Windows
   pip install fastapi[standart] openai sqlite-utils
   ```
   (Se já estiver usando o `venv/` existente, apenas ative-o.)

2. **Configurar a LLM (`backend/llm.py`)**
   - `usar_llm_local = True`: usa LM Studio via `base_url` + API key `"lm-studio"`.
   - `usar_llm_local = False`: habilita o cliente oficial OpenAI (preencha `api_key`).
   - Ajuste `modelo` conforme o endpoint escolhido (`openai/gpt-oss-20b`, `gpt-4o`, etc.).

3. **Subir o backend**
   ```bash
   fastapi dev backend/main.py
   ```
   O FastAPI faz:
   - Montagem automática de `/static` → arquivos web.
   - Criação do banco (`create_tables()`) antes de aceitar requisições.

4. **Acessar**
   - `http://localhost:8000/` mostra a landing page.
   - `http://localhost:8000/chat` abre o chat principal.

## Fluxo do Frontend

- `static/index.html` captura uma mensagem inicial e redireciona para `/chat?msg=...`.
- `static/chat.js`:
  - Busca conversas existentes em `/conversas`.
  - Cria conversas novas (`POST /conversas`) e, se necessário, faz isso automaticamente quando o usuário envia a primeira mensagem.
  - Envia mensagens (`POST /conversas/{id}/mensagens`) e renderiza tanto o usuário quanto a IA (com suporte a Markdown via `marked.js`).
  - Permite excluir conversas (`DELETE /conversas/{id}`) ou resetar o banco (`DELETE /api/db`).

## API do Backend

| Método & Rota                         | Descrição |
|--------------------------------------|-----------|
| `GET /`                              | Retorna `static/index.html`. |
| `GET /chat`                          | Retorna `static/chat.html`. |
| `GET /conversas`                     | Lista conversas (`conversa_id`, `titulo`, `data_criacao`). |
| `POST /conversas`                    | Cria nova conversa (`titulo`). |
| `GET /conversas/{id}/mensagens`      | Retorna mensagens ordenadas por `timestamp`. |
| `POST /conversas/{id}/mensagens`     | Salva mensagem do usuário, chama LLM e grava resposta. |
| `DELETE /conversas/{id}`             | Remove conversa e mensagens associadas (cascade). |
| `DELETE /api/db`                     | Limpa o arquivo SQLite e recria as tabelas (uso dev). |

### Limites e orçamento de contexto
`enviarMensagem()` recorta o histórico mais recente até 4.000 caracteres, adiciona um prompt de sistema e envia ao modelo via `enviarMensagemLLM()`.

## Banco de Dados

Tabela `conversas`
- `conversa_id` (PK autoincrement)
- `titulo`
- `data_criacao` (ISO string)

Tabela `mensagens`
- `mensagem_id` (PK autoincrement)
- `conversa_id` (FK → `conversas`, `ON DELETE CASCADE`)
- `remetente` (`Usuario` ou `IA`)
- `conteudo`
- `timestamp` (ISO string)

`backend/database/builddb.py` é chamado tanto no startup do FastAPI quanto no endpoint `DELETE /api/db`, garantindo idempotência.



