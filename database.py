import sqlite3
import random
import string

DB_NAME = "trep_hata_v3.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # 1. Таблица пользователей
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            nickname TEXT DEFAULT 'Бродяга',
            role TEXT DEFAULT 'Житель',
            hc REAL DEFAULT 5.0,
            aura INTEGER DEFAULT 10,
            tasks_done INTEGER DEFAULT 0,
            lies_count INTEGER DEFAULT 0,
            cases_opened INTEGER DEFAULT 0,
            equipped_json TEXT DEFAULT '{}',
            inventory_count INTEGER DEFAULT 2
        )
    """)

    # 2. Таблица всех чатов/групп (для рассылки опросов во все беседы)
    c.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            chat_id INTEGER PRIMARY KEY,
            title TEXT,
            chat_type TEXT
        )
    """)

    # 3. Таблица заданий на проверке (Правда / Пиздёж)
    c.execute("""
        CREATE TABLE IF NOT EXISTS polls (
            poll_id INTEGER PRIMARY KEY AUTOINCREMENT,
            creator_id INTEGER,
            creator_name TEXT,
            task_title TEXT,
            reward REAL,
            aura_bonus INTEGER,
            yes_voters TEXT DEFAULT '',
            yes_names TEXT DEFAULT '',
            no_voters TEXT DEFAULT '',
            status TEXT DEFAULT 'pending',
            claim_code TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Миграция на случай старой таблицы без yes_names
    try:
        c.execute("ALTER TABLE polls ADD COLUMN yes_names TEXT DEFAULT ''")
    except Exception:
        pass

    # 4. Таблица сообщений опросов во всех чатах
    c.execute("""
        CREATE TABLE IF NOT EXISTS poll_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            poll_id INTEGER,
            chat_id INTEGER,
            message_id INTEGER
        )
    """)

    # 5. Таблица общей бухгалтерии квартиры (Чеки, ЖКХ, Аренда)
    c.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payer_id INTEGER,
            payer_name TEXT,
            category TEXT DEFAULT 'Быт',
            amount REAL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def register_chat(chat_id: int, title: str, chat_type: str):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO chats (chat_id, title, chat_type) VALUES (?, ?, ?)",
        (chat_id, title or "Чат Треп Хаты", chat_type)
    )
    conn.commit()
    conn.close()


def get_all_chats():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT chat_id, title, chat_type FROM chats")
    rows = c.fetchall()
    conn.close()
    return rows


def ensure_user(user_id: int, username: str, first_name: str):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    if not c.fetchone():
        c.execute(
            "INSERT INTO users (user_id, username, nickname, role, hc, aura) VALUES (?, ?, ?, 'Житель', 5.0, 10)",
            (user_id, username or "", first_name or "Бродяга")
        )
        conn.commit()
    conn.close()


def get_aura_title(aura: int) -> str:
    if aura <= -30:
        return "🚽 Главный Опущенный Хаты"
    elif aura < 0:
        return "🐓 Опущенный (Аура в минусе)"
    elif aura < 15:
        return "😐 Серый Пассажир"
    elif aura < 40:
        return "🤝 Ровный Пацан"
    elif aura < 80:
        return "🔥 Уважаемый Кент"
    elif aura < 150:
        return "👑 Смотрящий за Треп Хатой"
    else:
        return "⚡ Святой Апостол Алхана"


def get_hc_rank(hc: float, aura: int) -> str:
    if aura < 0:
        return "🐓 Опущенный"
    if hc < 0:
        return "💩 Ебучий лох (Должник)"
    elif hc < 10:
        return "🤡 Дух Треп Хаты"
    elif hc < 25:
        return "🧹 Младший по тарелочкам"
    elif hc < 60:
        return "🍺 Барон Холодильника"
    elif hc < 120:
        return "💎 Магнат Шараги"
    else:
        return "👑 Император Треп Хаты"


def generate_claim_code(reward: float, aura: int) -> str:
    """
    Генерирует защищённый от подделки Пин-код формата: HATA-35-15-K8M2-7
    Внутри зашита точная награда (35 = 3.5 HC), аура (15) и контрольное число!
    """
    hc_int = max(5, min(99, int(round(reward * 10))))
    au_int = max(1, min(99, int(aura)))
    salt = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    ascii_sum = sum(ord(ch) for ch in salt)
    checksum = (hc_int * 3 + au_int * 7 + ascii_sum) % 36
    check_char = (string.digits + string.ascii_uppercase)[checksum]
    return f"HATA-{hc_int:02d}-{au_int:02d}-{salt}-{check_char}"


def estimate_custom_task_reward(text: str) -> tuple[float, int]:
    """
    ИИ-оценщик стоимости кастомного задания по ключевым словам и длине (1.0 - 5.0 HC, 5 - 30 Ауры)
    """
    t = (text or "").lower()
    hc = 1.5
    aura = 8

    high_words = [
        "ягер", "виск", "алко", "пив", "купил", "забашлял", "оплатил",
        "генеральн", "толчок", "унитаз", "плит", "шавух", "омлет", "закуп"
    ]
    med_words = [
        "мусор", "посуд", "приготов", "убрал", "пропылесос",
        "помыл", "магаз", "продукт", "смен", "полы", "ванн", "раковин"
    ]

    for w in high_words:
        if w in t:
            hc += 1.2
            aura += 6
    for w in med_words:
        if w in t:
            hc += 0.7
            aura += 4

    if len(t) > 25:
        hc += 0.5

    hc = round(min(max(hc, 1.0), 5.0) * 2) / 2
    aura = int(min(max(aura, 5), 30))
    return hc, aura


if __name__ == "__main__":
    init_db()
    print("✅ База данных trep_hata_v3.db успешно инициализирована!")