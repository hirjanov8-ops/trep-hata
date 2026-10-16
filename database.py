import sqlite3

DB_NAME = "trep_hata_v2.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Таблица пацанов
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            nickname TEXT DEFAULT 'Не зареган',
            role TEXT DEFAULT 'Житель',
            hc REAL DEFAULT 5.0,
            aura INTEGER DEFAULT 0,
            tasks_done INTEGER DEFAULT 0,
            lies_count INTEGER DEFAULT 0
        )
    """)
    
    # Таблица опросов Правда/Пиздёж
    c.execute("""
        CREATE TABLE IF NOT EXISTS polls (
            poll_id INTEGER PRIMARY KEY AUTOINCREMENT,
            creator_id INTEGER,
            creator_name TEXT,
            task_title TEXT,
            reward REAL,
            aura_bonus INTEGER,
            status TEXT DEFAULT 'pending'
        )
    """)
    
    # Таблица общака / чеков (для Кирилла)
    c.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payer_name TEXT,
            amount REAL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

def get_rank_title(hc: float, aura: int) -> str:
    if hc < 0:
        return "💩 Ебучий лох (В долгах)"
    score = hc + (aura * 0.5)
    if score < 8:
        return "🤡 Дух Треп Хаты"
    elif score < 20:
        return "🧹 Младший по тарелочкам"
    elif score < 45:
        return "🍺 Смотрящий за холодильником"
    elif score < 90:
        return "👑 Авторитет Треп Хаты"
    else:
        return "⚡ Наместник Алхана"