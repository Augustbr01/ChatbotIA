import aiosqlite    
from contextlib import asynccontextmanager

caminho_db = "backend/database/chatbot.db"

@asynccontextmanager
async def get_db_connection():
    conn = None
    try:
        conn = await aiosqlite.connect(caminho_db)
        yield conn
    finally:
        if conn:
            await conn.close()

async def get_db():
    async with get_db_connection() as conn:
        yield conn
