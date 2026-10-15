import sqlite3

DB_NAME = "trep_hata.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Пользователи (Саня, Карась, Кирилл)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            hc INTEGER DEFAULT 50,
            aura INTEGER DEFAULT 0,
            equipped_skin TEXT DEFAULT 'Штаны бомжа',
            equipped_acc TEXT DEFAULT 'Нет',
            equipped_head TEXT DEFAULT 'Нет'
        )
    """)
    
    # Инвентарь предметов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            item_name TEXT,
            item_type TEXT,
            rarity TEXT,
            sell_price REAL
        )
    """)
    
    # Активные задания на проверку (Правда/Ложь)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pending_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            task_desc TEXT,
            reward INTEGER
        )
    """)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()