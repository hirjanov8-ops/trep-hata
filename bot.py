import asyncio
import json
import random
import sqlite3
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from database import DB_NAME, init_db, get_rank_title

# ==========================================
# НАСТРОЙКИ (ВСТАВЬ СВОЙ ТОКЕН И ССЫЛКУ)
# ==========================================
TOKEN = "ТУТ_ТВОЙ_ТОКЕН_БОТА_ОТ_BOTFATHER"
WEBAPP_URL = "https://hirjanov8-ops.github.io/trep-hata/web_app/"

bot = Bot(token=TOKEN)
dp = Dispatcher()
init_db()

PUNISHMENTS = [
    "🚽 Драит толчок и раковину до блеска в соло без перчаток!",
    "🍳 Готовит фирменный Омлет Карася на всю хату завтра утром!",
    "🗑️ Выносит абсолютно весь мусор и пустые бутылки всю следующую неделю!",
    "🏃‍♂️ Бежит в магаз за Ягерем/Виски/энергетиками в любую погоду по первому зову пацанов!",
    "🍽️ Моет всю гору посуды и плиту после следующего бухича в одно рыло!",
    "🤡 Ставит себе статус «Любовница Пня и Птицы» на 48 часов в телеге!"
]

def ensure_user(user: types.User):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE user_id = ?", (user.id,))
    if not c.fetchone():
        c.execute(
            "INSERT INTO users (user_id, username, nickname, hc, aura) VALUES (?, ?, ?, 5.0, 0)",
            (user.id, user.username or "", user.first_name)
        )
        conn.commit()
    conn.close()

# --- ГЛАВНОЕ МЕНЮ И ОБУЧЕНИЕ ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    ensure_user(message.from_user)
    
    # Reply-клавиатура, которая передаёт данные из WebApp в бота
    rkb = ReplyKeyboardBuilder()
    rkb.button(
        text="🔥 ОТКРЫТЬ ТРЕП ХАТУ (Mini App)",
        web_app=types.WebAppInfo(url=WEBAPP_URL)
    )
    rkb.button(text="📊 Топ Хаты")
    rkb.button(text="📖 Все фишки бота")
    rkb.adjust(1, 2)

    ikb = InlineKeyboardBuilder()
    ikb.button(text="🚀 Запустить Mini App (Из чата)", web_app=types.WebAppInfo(url=WEBAPP_URL))
    ikb.button(text="🎓 Подробный мануал", callback_data="tutorial_chat")
    ikb.adjust(1)

    text = (
        "🏠 **СИСТЕМА «ТРЕП ХАТА v2.0» ЗАПУЩЕНА!**\n\n"
        "Здарова, бродяга! Это официальный пульт управления вашей хатой (Саня Жиросан, Карась и Кирилл Карлик Джексон).\n"
        "Стартовый баланс каждого при регистрации: **5.0 HC (ХатаКойнов)**.\n\n"
        "👇 **Жми кнопку ниже, чтобы пройти регистрацию, одеть своего манекена, покрутить кейсы или сдать квест!**"
    )
    await message.answer(text, reply_markup=rkb.as_markup(resize_keyboard=True), parse_mode="Markdown")
    await message.answer("Быстрый доступ:", reply_markup=ikb.as_markup())

# --- СПРАВКА ПО ВСЕМ ФИШКАМ ЧАТА ---
@dp.message(Command("help_bot"))
@dp.message(F.text == "📖 Все фишки бота")
async def cmd_help_bot(message: types.Message):
    text = (
        "📖 **ПОЛНЫЙ ГАЙД: ЧТО УМЕЕТ БОТ В ЧАТЕ И MINI APP**\n\n"
        "🔹 **1. Проверка дел (Правда или Пиздёж):**\n"
        "В Mini App (или командой `/claim`) выбираешь дело: убрался, приготовил омлет Карася, принёс Ягерь/Виски. "
        "Бот кидает опрос в чат. Достаточно **1 голоса «Правда»** от кента — и ты получаешь **+1..+5 HC** и **Ауру**! "
        "Если нажали **«Пиздёж»** — с тебя списывают **-3 HC** штрафа!\n\n"
        "🔹 **2. Личный Манекен, Кейсы и Апгрейд (Внутри Mini App):**\n"
        "• У каждого свой перс. Выбивай шмотки (*Трусы Карася*, *Цепь Джексона*, *Футболка Жиросана*, *Корона Алхана*) и надевай — они **реально отображаются на манекене**.\n"
        "• Перед прокрутом кейса видно весь лут внутри.\n"
        "• В **Апгрейде** ставь шмотку под **10% / 30% / 50% / 75%**. Выиграл — старая пропала, новая появилась. Проиграл — шмотка сгорела нахуй!\n\n"
        "🔹 **3. Команды для общего чата:**\n"
        "• `/claim` — Быстро создать опрос о выполненном деле прямо в чате\n"
        "• `/aura @ник` (или ответом на сообщение) — Накинуть **+10 Ауры** кенту за базар или поступок\n"
        "• `/shame @ник` (или ответом) — Снять **-5 Ауры** за крысятничество или душноту\n"
        "• `/split 1500 Закупка еды` — Калькулятор Кирилла: делит чек на троих и даёт тебе +2 HC\n"
        "• `/top` — Таблица лидеров, балансов, рангов и должников\n"
        "• `/court` — **Воскресный Суд**: крутит барабан наказаний для тех, у кого баланс меньше 0!"
    )
    await message.answer(text, parse_mode="Markdown")

@dp.callback_query(F.data == "tutorial_chat")
async def cb_tutorial(call: types.CallbackQuery):
    await cmd_help_bot(call.message)
    await call.answer()

# --- БЫСТРОЕ СОЗДАНИЕ ЗАДАНИЯ В ЧАТЕ (/claim) ---
@dp.message(Command("claim"))
async def cmd_claim(message: types.Message):
    ensure_user(message.from_user)
    ikb = InlineKeyboardBuilder()
    tasks = [
        ("🍳 Приготовил Омлет Карася (+3 HC)", "task_omlet_3_15"),
        ("🧹 Убрался в хате / Вынес мусор (+2 HC)", "task_clean_2_10"),
        ("🍽️ Помыл всю гору посуды (+2 HC)", "task_dishes_2_10"),
        ("🦌 Купил Ягерь / Виски пацанам (+5 HC)", "task_alko_5_25"),
        ("🛒 Сгонял за продуктами в магаз (+3 HC)", "task_shop_3_15"),
        ("💰 Заработал больше всех за смену (+4 HC)", "task_work_4_20"),
    ]
    for title, cb in tasks:
        ikb.button(text=title, callback_data=cb)
    ikb.adjust(1)
    await message.answer(
        f"⚡ **{message.from_user.first_name}**, выбери, что ты реально сделал (пацаны проверят):",
        reply_markup=ikb.as_markup(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data.startswith("task_"))
async def cb_create_poll(call: types.CallbackQuery):
    parts = call.data.split("_")
    code, reward, aura = parts[1], float(parts[2]), int(parts[3])
    titles = {
        "omlet": "Приготовил фирменный Омлет Карася 🍳",
        "clean": "Убрался в хате и вынес мусор 🧹",
        "dishes": "Помыл всю посуду и плиту 🍽️",
        "alko": "Купил Ягерь / Виски / подгон на хату 🦌🥃",
        "shop": "Сгонял в магаз за продуктами 🛒",
        "work": "Отработал смену и занёс бабки в общак 💰"
    }
    task_title = titles.get(code, "Выполнил дело по хате")
    user = call.from_user
    ensure_user(user)

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "INSERT INTO polls (creator_id, creator_name, task_title, reward, aura_bonus) VALUES (?, ?, ?, ?, ?)",
        (user.id, user.first_name, task_title, reward, aura)
    )
    poll_id = c.lastrowid
    conn.commit()
    conn.close()

    ikb = InlineKeyboardBuilder()
    ikb.button(text=f"✅ Правда (+{reward:g} HC)", callback_data=f"vote_yes_{poll_id}")
    ikb.button(text="❌ Пиздёж (-3 HC штраф)", callback_data=f"vote_no_{poll_id}")
    ikb.adjust(2)

    await call.message.edit_text(
        f"🚨 **ПРОВЕРКА НА ПИЗДЁЖ #{poll_id}** 🚨\n\n"
        f"👤 Заявитель: **{user.first_name}**\n"
        f"📋 Утверждает, что: **{task_title}**\n"
        f"💎 Награда: **+{reward:g} HC** и **+{aura} Ауры**\n\n"
        f"*Нужен 1 голос от соседа (сам за себя голосовать не можешь)!*",
        reply_markup=ikb.as_markup(),
        parse_mode="Markdown"
    )
    await call.answer("Опрос отправлен в чат!")

@dp.callback_query(F.data.startswith("vote_"))
async def cb_vote_poll(call: types.CallbackQuery):
    _, decision, poll_id_str = call.data.split("_")
    poll_id = int(poll_id_str)
    voter = call.from_user
    ensure_user(voter)

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT creator_id, creator_name, task_title, reward, aura_bonus, status FROM polls WHERE poll_id = ?", (poll_id,))
    row = c.fetchone()

    if not row:
        conn.close()
        return await call.answer("Опрос не найден!", show_alert=True)

    creator_id, creator_name, task_title, reward, aura_bonus, status = row

    if status != "pending":
        conn.close()
        return await call.answer("Этот опрос уже закрыт!", show_alert=True)

    # Проверка: нельзя голосовать за самого себя
    if voter.id == creator_id:
        conn.close()
        return await call.answer("Хитрожопый? Сам за себя голосовать нельзя, жди Карася или Кирилла!", show_alert=True)

    if decision == "yes":
        c.execute("UPDATE polls SET status = 'approved' WHERE poll_id = ?", (poll_id,))
        c.execute(
            "UPDATE users SET hc = hc + ?, aura = aura + ?, tasks_done = tasks_done + 1 WHERE user_id = ?",
            (reward, aura_bonus, creator_id)
        )
        c.execute("SELECT hc, aura FROM users WHERE user_id = ?", (creator_id,))
        new_hc, new_aura = c.fetchone()
        conn.commit()
        conn.close()

        await call.message.edit_text(
            f"✅ **ПОДТВЕРЖДЕНО ПАЦАНАМИ!**\n\n"
            f"👤 Красавчик: **{creator_name}**\n"
            f"📋 Дело: **{task_title}**\n"
            f"⚖️ Подтвердил: **{voter.first_name}**\n"
            f"💰 Начислено: **+{reward:g} HC** и **+{aura_bonus} Ауры**!\n"
            f"🏦 Баланс в БД чата: **{new_hc:.1f} HC** | ✨ Аура: **{new_aura}**",
            parse_mode="Markdown"
        )
        await call.answer("Засчитано!")
    else:
        penalty = 3.0
        c.execute("UPDATE polls SET status = 'rejected' WHERE poll_id = ?", (poll_id,))
        c.execute(
            "UPDATE users SET hc = hc - ?, aura = aura - 15, lies_count = lies_count + 1 WHERE user_id = ?",
            (penalty, creator_id)
        )
        c.execute("SELECT hc, aura FROM users WHERE user_id = ?", (creator_id,))
        new_hc, new_aura = c.fetchone()
        conn.commit()
        conn.close()

        await call.message.edit_text(
            f"🚨 **ПОЙМАН НА ПИЗДЕЖЕ!** 🚨\n\n"
            f"🤡 Скаммер: **{creator_name}** пытался наебать хату ({task_title})!\n"
            f"🕵️‍♂️ Разоблачил: **{voter.first_name}**\n"
            f"📉 Штраф: **-{penalty:g} HC** и **-15 Ауры**!\n"
            f"🏦 Баланс теперь: **{new_hc:.1f} HC** (Если к воскресенью меньше 0 — ждёт Суд!)",
            parse_mode="Markdown"
        )
        await call.answer("Скаммер наказан!")

# --- ПРИЁМ ДАННЫХ ИЗ MINI APP (СИНХРОНИЗАЦИЯ И ОПРОСЫ) ---
@dp.message(F.web_app_data)
async def handle_webapp_data(message: types.Message):
    ensure_user(message.from_user)
    try:
        data = json.loads(message.web_app_data.data)
    except Exception:
        return

    action = data.get("action")
    user = message.from_user

    if action == "sync_profile":
        nickname = data.get("nickname", user.first_name)
        role = data.get("role", "Житель")
        hc = float(data.get("hc", 5.0))
        aura = int(data.get("aura", 0))

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute(
            "UPDATE users SET nickname = ?, role = ?, hc = ?, aura = ? WHERE user_id = ?",
            (nickname, role, hc, aura, user.id)
        )
        conn.commit()
        conn.close()

        outfit = data.get("outfit", {})
        await message.answer(
            f"🔄 **Профиль синхронизирован с Треп Хатой!**\n\n"
            f"👤 Ник: **{nickname}** ({role})\n"
            f"💰 Баланс: **{hc:.1f} HC** | ✨ Аура: **{aura}**\n"
            f"🎩 Голова: *{outfit.get('head', 'Нет')}*\n"
            f"👓 Лицо: *{outfit.get('face', 'Нет')}*\n"
            f"👕 Торс: *{outfit.get('body', 'Нет')}*\n"
            f"🩲 Ноги: *{outfit.get('legs', 'Нет')}*\n"
            f"⛓️ Аксессуар: *{outfit.get('acc', 'Нет')}*",
            parse_mode="Markdown"
        )

    elif action == "create_task_poll":
        task_title = data.get("title", "Дело по хате")
        reward = float(data.get("reward", 2.0))
        aura = int(data.get("aura", 10))

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute(
            "INSERT INTO polls (creator_id, creator_name, task_title, reward, aura_bonus) VALUES (?, ?, ?, ?, ?)",
            (user.id, user.first_name, task_title, reward, aura)
        )
        poll_id = c.lastrowid
        conn.commit()
        conn.close()

        ikb = InlineKeyboardBuilder()
        ikb.button(text=f"✅ Правда (+{reward:g} HC)", callback_data=f"vote_yes_{poll_id}")
        ikb.button(text="❌ Пиздёж (-3 HC)", callback_data=f"vote_no_{poll_id}")
        ikb.adjust(2)

        await message.answer(
            f"📲 **ЗАЯВКА ИЗ MINI APP #{poll_id}**\n\n"
            f"👤 **{user.first_name}** заявляет: **{task_title}**\n"
            f"💎 Награда: **+{reward:g} HC** и **+{aura} Ауры**\n\n"
            f"Пацаны, подтверждаем?",
            reply_markup=ikb.as_markup(),
            parse_mode="Markdown"
        )

# --- СИСТЕМА АУРЫ В ЧАТЕ ---
@dp.message(Command("aura"))
async def cmd_aura(message: types.Message):
    ensure_user(message.from_user)
    if not message.reply_to_message:
        return await message.answer("☝️ Чтобы накинуть **+10 Ауры**, ответь (reply) этой командой `/aura` на сообщение кента!", parse_mode="Markdown")
    
    target = message.reply_to_message.from_user
    if target.id == message.from_user.id:
        return await message.answer("Сам себе ауру надрачивать не выйдет, бро 🤡")
    
    ensure_user(target)
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET aura = aura + 10 WHERE user_id = ?", (target.id,))
    c.execute("SELECT aura FROM users WHERE user_id = ?", (target.id,))
    new_aura = c.fetchone()[0]
    conn.commit()
    conn.close()

    await message.answer(
        f"✨ **{message.from_user.first_name}** выразил респект **{target.first_name}**!\n"
        f"📈 Аура **{target.first_name}** выросла на **+10** (Всего: **{new_aura} ✨**)",
        parse_mode="Markdown"
    )

@dp.message(Command("shame"))
async def cmd_shame(message: types.Message):
    if not message.reply_to_message:
        return await message.answer("☝️ Ответь (reply) командой `/shame` на сообщение того, кто насрал в душу или ведёт себя как Пень/Птица!")
    
    target = message.reply_to_message.from_user
    ensure_user(target)
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET aura = aura - 10 WHERE user_id = ?", (target.id,))
    c.execute("SELECT aura FROM users WHERE user_id = ?", (target.id,))
    new_aura = c.fetchone()[0]
    conn.commit()
    conn.close()

    await message.answer(
        f"💩 **{message.from_user.first_name}** опустил ауру **{target.first_name}** на **-10**!\n"
        f"📉 Текущая аура: **{new_aura} ✨**",
        parse_mode="Markdown"
    )

# --- СПЛИТТЕР ЧЕКОВ ДЛЯ КИРИЛЛА УМНОГО ---
@dp.message(Command("split"))
async def cmd_split(message: types.Message):
    ensure_user(message.from_user)
    parts = message.text.split(maxsplit=2)
    if len(parts) < 2:
        return await message.answer("🧮 **Формат Кирилла Умного:**\nПиши `/split 1500 Продукты и омлет` — бот поделит сумму на троих и даст тебе +2 HC за закупку!", parse_mode="Markdown")
    
    try:
        amount = float(parts[1])
    except ValueError:
        return await message.answer("Сумма должна быть числом! Пример: `/split 1200 Пиво и яйца`", parse_mode="Markdown")
    
    desc = parts[2] if len(parts) > 2 else "Общая закупка на хату"
    per_person = round(amount / 3, 2)

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO expenses (payer_name, amount, description) VALUES (?, ?, ?)", (message.from_user.first_name, amount, desc))
    c.execute("UPDATE users SET hc = hc + 2, aura = aura + 5 WHERE user_id = ?", (message.from_user.id,))
    conn.commit()
    conn.close()

    await message.answer(
        f"🧾 **ЧЕК ЗАФИКСИРОВАН (Бухгалтерия Карлика Джексона)**\n\n"
        f"💳 Оплатил: **{message.from_user.first_name}**\n"
        f"🛒 Покупка: **{desc}**\n"
        f"💰 Общая сумма: **{amount:g} ₽**\n"
        f"➗ **С каждого из остальных двоих по: {per_person:g} ₽** (скинуть {message.from_user.first_name})\n\n"
        f"🎁 За суету с закупкой **{message.from_user.first_name}** получает **+2 HC** и **+5 Ауры**!",
        parse_mode="Markdown"
    )

# --- ТОП ХАТЫ ---
@dp.message(Command("top"))
@dp.message(F.text == "📊 Топ Хаты")
async def cmd_top(message: types.Message):
    ensure_user(message.from_user)
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT nickname, username, role, hc, aura, tasks_done, lies_count FROM users ORDER BY hc DESC, aura DESC")
    rows = c.fetchall()
    conn.close()

    text = "🏆 **РЕЙТИНГ ТРЕП ХАТЫ (САМЫЕ ПИЗДАТЫЕ И ЕБУЧИЕ ЛОХИ):**\n\n"
    for idx, (nick, uname, role, hc, aura, tasks, lies) in enumerate(rows, 1):
        rank = get_rank_title(hc, aura)
        medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else "🔸"
        text += (
            f"{medal} **{idx}. {nick}** ({role})\n"
            f"   💰 Баланс: **{hc:.1f} HC** | ✨ Аура: **{aura}**\n"
            f"   🎖️ Уровень: *{rank}*\n"
            f"   ✅ Дел сделано: {tasks} | 🤡 Спиздел: {lies} раз\n\n"
        )
    await message.answer(text, parse_mode="Markdown")

# --- ВОСКРЕСНЫЙ СУД (БАРАБАН НАКАЗАНИЙ) ---
@dp.message(Command("court"))
async def cmd_court(message: types.Message):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT user_id, nickname, hc FROM users WHERE hc < 0")
    debtors = c.fetchall()
    conn.close()

    if not debtors:
        return await message.answer(
            "⚖️ **ВОСКРЕСНЫЙ СУД ТРЕП ХАТЫ:**\n\n"
            "Проверил балансы — сегодня ни одного **Ебучего лоха** с минусовым балансом нет! Все пацаны при койнах, Алхан доволен. 🙏",
            parse_mode="Markdown"
        )

    text = "⚖️🔥 **ВОСКРЕСНЫЙ СУД ТРЕП ХАТЫ!** 🔥⚖️\n\nОбнаружены должники с минусовым балансом! Крутим барабан наказаний:\n\n"
    for uid, nick, hc in debtors:
        punish = random.choice(PUNISHMENTS)
        text += (
            f"💀 Должник: **{nick}** (Баланс: **{hc:.1f} HC**)\n"
            f"🔨 **Приговор:** {punish}\n\n"
        )
    text += "*После выполнения наказания пацаны могут обнулить долг через `/claim`!*"
    await message.answer(text, parse_mode="Markdown")

async def main():
    print("🔥 Бот ТРЕП ХАТА v2.0 запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())