import aiosqlite
import asyncio

caminho_db = "backend/database/chatbot.db"


async def create_tables():

    async with aiosqlite.connect(caminho_db) as db:
        await db.execute("PRAGMA foreign_keys = ON;")


        # --- Tabela CONVERSAS ---
        await db.execute('''
            CREATE TABLE IF NOT EXISTS conversas (
                conversa_id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL, 
                data_criacao TEXT NOT NULL
            );
        ''')

        # --- Tabela MENSAGENS ---
        await db.execute('''
            CREATE TABLE IF NOT EXISTS mensagens (
                mensagem_id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversa_id INTEGER NOT NULL, 
                remetente TEXT NOT NULL,
                conteudo TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                        
                FOREIGN KEY (conversa_id) REFERENCES conversas(conversa_id)
                        ON DELETE CASCADE
            );
        ''')

        await db.commit()
        print("INFO:     ✅ Banco de dados inicializado com sucesso.")

async def initialize_db():
    await create_tables()   # <-- SEM asyncio.run()