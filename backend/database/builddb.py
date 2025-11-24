import sqlite3

def create_tables():
    # Garantir que a conexão usa o modo WAL para melhor concorrência (opcional, mas recomendado)
    conn = sqlite3.connect("backend/database/chatbot.db")
    cursor = conn.cursor()

    # --- Tabela CONVERSAS ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversas (
            conversa_id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL, 
            data_criacao TEXT NOT NULL
        );
    ''')

    # --- Tabela MENSAGENS ---
    cursor.execute('''
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

    conn.commit()
    conn.close()
    print("INFO:     ✅ Banco de dados inicializado com sucesso.")