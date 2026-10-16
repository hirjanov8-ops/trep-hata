import asyncio
import json
import random
import sqlite3
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from database import DB_NAME, init_db, register_chat, get_all_chats, ensure_user, get_aura_title, get_hc_rank, generate_claim_code, estimate_custom_task_reward

# =========================================================================
# НАСТРОЙКИ (ВСТАВЬ СВОЙ ТОКЕН И ССЫЛКУ GITHUB PAGES)
# =========================================================================
TOKEN = "ТУТ_ТВОЙ_ТОКЕН_БОТА_ОТ_BOTFATHER"
WEBAPP_URL = "https://hirjanov8-ops.github.io/trep-hata/web_app/"

bot = Bot(token=TOKEN)
dp = Dispatcher()
init_db()

PUNISHMENTS = [
    "🚽 Драит туалет и раковину в соло до зеркального блеска без перчаток!",
    "🍳 Готовит фирменный Омлет Карася на всю хату завтра утром в 8:00!",
    "🗑️ Выносит весь мусор, коробки и пустые бутылки всю неделю!",
    "🏃‍♂️ Срывается в магаз за Ягерем / Виски / энергетиками в любую погоду!",
    "🍽️ Моет всю гору посуды, плиту и сковородки после каждого бухича в одно рыло!",
    "🤡 Носит позорный статус «🐓 Главный Опущенный Хаты» в телеге 48 часов!"
]

# --- РЕГИСТРАЦИЯ ЧАТОВ И ПОЛЬЗОВАТЕЛЕЙ ПРИ ЛЮБОМ СООБЩЕНИИ ---
@dp.message()
async def middleware_handler(message: types.Message):
    if message.chat.type in ["group", "supergroup"]:
        register_chat(message.chat.id, message.chat.title, message.chat.type)
    if message.from_user:
        ensure_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    if message.text and message.text.startswith("/"):
        return

# --- /start И ГЛАВНОЕ МЕНЮ ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if message.chat.type in ["group", "supergroup"]:
        register_chat(message.chat.id, message.chat.title, message.chat.type)
    ensure_user(message.from_user.id, message.from_user.username, message.from_user.first_name)

    rkb = ReplyKeyboardBuilder()
    rkb.button(text="🔥 ОТКРЫТЬ ТРЕП ХАТУ (Mini App)", web_app=types.WebAppInfo(url=WEBAPP_URL))
    rkb.button(text="📊 Топ Хаты")
    rkb.button(text="📖 Все фишки бота")
    rkb.adjust(1, 2)

    ikb = InlineKeyboardBuilder()
    ikb.button(text="🚀 Запустить Mini App", web_app=types.WebAppInfo(url=WEBAPP_URL))
    ikb.adjust(1)

    text = (
        "🏠 **СИСТЕМА «ТРЕП ХАТА v3.0 PRO» АКТИВИРОВАНА!**\n\n"
        "Здарова, бродяга! Это пульт управления нашей хатой (Саня Жиросан, Карась, Кирилл Карлик Джексон).\n"
        "Стартовый баланс: **5.0 HC**.\n"
        "✨ Теперь Аура реально решает: уйдёшь в минус — станешь опущенным с дебаффами!\n\n"
        "👇 **Жми кнопку ниже, чтобы запустить приложение, крутить рулетки, одевать манекена Майкла Джексона или создавать задания!**"
    )
    await message.answer(text, reply_markup=rkb.as_markup(resize_keyboard=True), parse_mode="Markdown")

# --- СПРАВКА /help_bot ---
@dp.message(Command("help_bot"))
@dp.message(F.text == "📖 Все фишки бота")
async def cmd_help_bot(message: types.Message):
    text = (
        "📖 **МАНУАЛ ПО ТРЕП ХАТЕ v3.0:**\n\n"
        "1️⃣ **Опросы «Правда или Пиздёж» во всех чатах:**\n"
        "Когда ты заявляешь дело в Mini App или через `/claim`, бот рассылает опрос **во все чаты хаты**. Чтобы задание засчиталось, нужно **ровно 2 голоса «Правда»** от соседей (сам за себя голосовать нельзя). После 2 голосов выдаётся Пин-код!\n\n"
        "2️⃣ **Система Ауры и Опущенных:**\n"
        "За добрые дела получаешь Ауру. Если Аура уходит в `< 0`, ты получаешь статус **«🐓 Опущенный»** (кейсы дороже на 25%, шанс апгрейда режется). Поднять ауру можно через `/aura @ник`.\n\n"
        "3️⃣ **Калькулятор сплита (`/split`):**\n"
        "Вбиваешь `/split 1800 Пиво и закупка` — бот делит сумму на троих (по 600 ₽ с каждого кента) и начисляет тебе +2 HC.\n\n"
        "4️⃣ **Рулетки, 50+ шмоток и Фулл Сет Майкла Джексона:**\n"
        "В Mini App крути Ежедневные и Еженедельные рулетки (с шансом 0.15% выпадения ультра-приза за 50 HC), открывай кейсы с пачками койнов, крафти шмот в апгрейде 10/30/50/75% с круговой анимацией и одевай манекена!"
    )
    await message.answer(text, parse_mode="Markdown")

# --- СОЗДАНИЕ ОПРОСА ЧЕРЕЗ /claim ---
@dp.message(Command("claim"))
async def cmd_claim(message: types.Message):
    ensure_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    parts = message.text.split(maxsplit=1)
    
    if len(parts) < 2:
        return await message.answer(
            "📋 **Как создать задание:**\n"
            "Напиши так: `/claim Сгонял в магазин за шавухой и энергетиками`\n"
            "Бот сам оценит сложность, выдаст цену в HC и Ауру, и разошлет опрос во все чаты!",
            parse_mode="Markdown"
        )
    
    task_desc = parts[1]
    reward, aura = estimate_custom_task_reward(task_desc)
    user = message.from_user

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "INSERT INTO polls (creator_id, creator_name, task_title, reward, aura_bonus) VALUES (?, ?, ?, ?, ?)",
        (user.id, user.first_name, task_desc, reward, aura)
    )
    poll_id = c.lastrowid
    conn.commit()
    conn.close()

    chats = get_all_chats()
    ikb = InlineKeyboardBuilder()
    ikb.button(text=f"✅ Правда (+{reward:g} HC)", callback_data=f"vote_yes_{poll_id}")
    ikb.button(text="❌ Пиздёж (-3 HC)", callback_data=f"vote_no_{poll_id}")
    ikb.adjust(2)

    poll_text = (
        f"🚨 **ПРОВЕРКА ДЕЛА #{poll_id}** 🚨\n\n"
        f"👤 Заявитель: **{user.first_name}**\n"
        f"📋 Задача: **{task_desc}**\n"
        f"💎 Награда: **+{reward:g} HC** | ✨ **+{aura} Ауры**\n\n"
        f"⚖️ *Нужно ровно 2 голоса «Правда» от соседей (сейчас: 0/2)!*"
    )

    sent_count = 0
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    for chat_id, title, _ in chats:
        try:
            msg = await bot.send_message(chat_id, poll_text, reply_markup=ikb.as_markup(), parse_mode="Markdown")
            c.execute("INSERT INTO poll_messages (poll_id, chat_id, message_id) VALUES (?, ?, ?)", (poll_id, chat_id, msg.message_id))
            sent_count += 1
        except Exception:
            pass

    conn.commit()
    conn.close()
    await message.answer(f"✅ Заявка создана и разослана в {sent_count} чатов хаты! Ждём 2 голоса пацанов.")

# --- ОБРАБОТКА ГОЛОСОВАНИЯ (РОВНО 2 ГОЛОСА + ЗАЩИТА ОТ САМОЛАЙКА) ---
@dp.callback_query(F.data.startswith("vote_"))
async def cb_vote(call: types.CallbackQuery):
    _, decision, poll_id_str = call.data.split("_")
    poll_id = int(poll_id_str)
    voter = call.from_user
    ensure_user(voter.id, voter.username, voter.first_name)

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT creator_id, creator_name, task_title, reward, aura_bonus, yes_voters, no_voters, status FROM polls WHERE poll_id = ?", (poll_id,))
    row = c.fetchone()

    if not row:
        conn.close()
        return await call.answer("Опрос не найден!", show_alert=True)

    creator_id, creator_name, task_title, reward, aura_bonus, yes_voters_str, no_voters_str, status = row

    if status != "pending":
        conn.close()
        return await call.answer("Этот опрос уже завершён!", show_alert=True)

    if voter.id == creator_id:
        conn.close()
        return await call.answer("Сам за себя голосовать нельзя, хитрожопый бродяга!", show_alert=True)

    yes_list = [int(x) for x in yes_voters_str.split(",") if x]
    no_list = [int(x) for x in no_voters_str.split(",") if x]

    if voter.id in yes_list or voter.id in no_list:
        conn.close()
        return await call.answer("Ты уже отдал свой голос в этом опросе!", show_alert=True)

    if decision == "yes":
        yes_list.append(voter.id)
    else:
        no_list.append(voter.id)

    new_yes_str = ",".join(map(str, yes_list))
    new_no_str = ",".join(map(str, no_list))

    if len(no_list) >= 1:
        c.execute("UPDATE polls SET status = 'rejected', no_voters = ? WHERE poll_id = ?", (new_no_str, poll_id))
        c.execute("UPDATE users SET hc = hc - 3.0, aura = aura - 20, lies_count = lies_count + 1 WHERE user_id = ?", (creator_id,))
        conn.commit()

        result_text = (
            f"❌ **ПОЙМАН НА ПИЗДЕЖЕ (#{poll_id})!**\n\n"
            f"🤡 Скаммер: **{creator_name}** ({task_title})\n"
            f"📉 Сосед проголосовал против: штраф **-3.0 HC** и **-20 Ауры**!"
        )
    elif len(yes_list) >= 2:
        claim_code = generate_claim_code("HATA")
        c.execute("UPDATE polls SET status = 'approved', yes_voters = ?, claim_code = ? WHERE poll_id = ?", (new_yes_str, claim_code, poll_id))
        c.execute("UPDATE users SET hc = hc + ?, aura = aura + ?, tasks_done = tasks_done + 1 WHERE user_id = ?", (reward, aura_bonus, creator_id))
        conn.commit()

        result_text = (
            f"✅ **ДЕЛО ОДОБРЕНО ПАЦАНАМИ (#{poll_id})!**\n\n"
            f"👤 Герой: **{creator_name}**\n"
            f"📋 Задача: **{task_title}**\n"
            f"💎 Выплачено: **+{reward:g} HC** и **+{aura_bonus} Ауры**!\n"
            f"🔑 Пин-код активации: `{claim_code}`"
        )
    else:
        c.execute("UPDATE polls SET yes_voters = ?, no_voters = ? WHERE poll_id = ?", (new_yes_str, new_no_str, poll_id))
        conn.commit()
        conn.close()
        await call.answer(f"Голос принят! («Правда»: {len(yes_list)}/2)")
        return

    c.execute("SELECT chat_id, message_id FROM poll_messages WHERE poll_id = ?", (poll_id,))
    msg_rows = c.fetchall()
    conn.close()

    for chat_id, msg_id in msg_rows:
        try:
            await bot.edit_message_text(result_text, chat_id=chat_id, message_id=msg_id, parse_mode="Markdown")
        except Exception:
            pass

    await call.answer("Голос учтён и итог подведён!")

# --- СИНХРОНИЗАЦИЯ ИЗ MINI APP ---
@dp.message(F.web_app_data)
async def handle_webapp_data(message: types.Message):
    ensure_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
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

        aura_title = get_aura_title(aura)
        await message.answer(
            f"🔄 **Профиль синхронизирован с Треп Хатой!**\n\n"
            f"👤 Ник: **{nickname}** ({role})\n"
            f"💰 Баланс: **{hc:.1f} HC** | ✨ Аура: **{aura}** ({aura_title})",
            parse_mode="Markdown"
        )

# --- СИСТЕМА АУРЫ И ОПУЩЕННЫХ (/aura И /shame) ---
@dp.message(Command("aura"))
async def cmd_aura(message: types.Message):
    if not message.reply_to_message:
        return await message.answer("☝️ Ответь (reply) командой `/aura` на сообщение кента, чтобы накинуть ему +15 Ауры!", parse_mode="Markdown")
    
    target = message.reply_to_message.from_user
    if target.id == message.from_user.id:
        return await message.answer("Сам себе ауру не накрутишь, бродяга 🤡")

    ensure_user(target.id, target.username, target.first_name)
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET aura = aura + 15 WHERE user_id = ?", (target.id,))
    c.execute("SELECT aura FROM users WHERE user_id = ?", (target.id,))
    new_aura = c.fetchone()[0]
    conn.commit()
    conn.close()

    status_title = get_aura_title(new_aura)
    await message.answer(
        f"✨ **{message.from_user.first_name}** выразил мощный респект **{target.first_name}**!\n"
        f"📈 Аура выросла до **{new_aura} ✨**\n"
        f"🎖️ Новый статус: *{status_title}*",
        parse_mode="Markdown"
    )

@dp.message(Command("shame"))
async def cmd_shame(message: types.Message):
    if not message.reply_to_message:
        return await message.answer("☝️ Ответь (reply) командой `/shame` на сообщение того, кто ведет себя как Пень или Птица!")
    
    target = message.reply_to_message.from_user
    ensure_user(target.id, target.username, target.first_name)
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET aura = aura - 20 WHERE user_id = ?", (target.id,))
    c.execute("SELECT aura FROM users WHERE user_id = ?", (target.id,))
    new_aura = c.fetchone()[0]
    conn.commit()
    conn.close()

    status_title = get_aura_title(new_aura)
    warning = " 🐓 **ВНИМАНИЕ: Чел улетел в минус по ауре и стал Опущенным!**" if new_aura < 0 else ""
    await message.answer(
        f"💩 **{message.from_user.first_name}** опустил ауру **{target.first_name}** на **-20**!\n"
        f"📉 Текущая аура: **{new_aura} ✨** ({status_title}){warning}",
        parse_mode="Markdown"
    )

# --- КАЛЬКУЛЯТОР СПЛИТА / КАУНТЕР ХАТЫ (/split) ---
@dp.message(Command("split"))
async def cmd_split(message: types.Message):
    parts = message.text.split(maxsplit=2)
    if len(parts) < 2:
        return await message.answer(
            "🧮 **Формула сплита для Кирилла Умного:**\n"
            "Пиши: `/split 1800 Закупка продуктов на неделю`\n"
            "Бот разделит сумму на троих и зафиксирует чек!",
            parse_mode="Markdown"
        )
    
    try:
        amount = float(parts[1])
    except ValueError:
        return await message.answer("Сумма должна быть числом! Пример: `/split 1500 Пицца`")

    desc = parts[2] if len(parts) > 2 else "Общая закупка"
    per_person = round(amount / 3, 2)

    ensure_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO expenses (payer_id, payer_name, amount, description) VALUES (?, ?, ?, ?)", (message.from_user.id, message.from_user.first_name, amount, desc))
    c.execute("UPDATE users SET hc = hc + 2.0, aura = aura + 10 WHERE user_id = ?", (message.from_user.id,))
    conn.commit()
    conn.close()

    await message.answer(
        f"🧾 **БУХГАЛТЕРИЯ ТРЕП ХАТЫ (Сплит чека)**\n\n"
        f"💳 Оплатил: **{message.from_user.first_name}**\n"
        f"🛒 Статья: **{desc}**\n"
        f"💰 Всего: **{amount:g} ₽**\n"
        f"➗ **С каждого из двоих соседей по: {per_person:g} ₽**\n\n"
        f"🎁 За суету с оплатой **{message.from_user.first_name}** получает **+2.0 HC** и **+10 Ауры**!",
        parse_mode="Markdown"
    )

# --- ТОП ХАТЫ ---
@dp.message(Command("top"))
@dp.message(F.text == "📊 Топ Хаты")
async def cmd_top(message: types.Message):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT nickname, role, hc, aura, tasks_done, lies_count FROM users ORDER BY hc DESC, aura DESC")
    rows = c.fetchall()
    conn.close()

    text = "🏆 **ДОСКА ПОЧЁТА И ЕБУЧИХ ЛОХОВ ТРЕП ХАТЫ:**\n\n"
    for idx, (nick, role, hc, aura, tasks, lies) in enumerate(rows, 1):
        medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else "🔸"
        hc_rank = get_hc_rank(hc, aura)
        aura_title = get_aura_title(aura)
        text += (
            f"{medal} **{idx}. {nick}** ({role})\n"
            f"   💰 Баланс: **{hc:.1f} HC** | ✨ Аура: **{aura}**\n"
            f"   🎖️ Ранг: *{hc_rank}* | Статус: *{aura_title}*\n"
            f"   ✅ Дел сделано: {tasks} | 🤡 Пиздежа: {lies}\n\n"
        )
    await message.answer(text, parse_mode="Markdown")

# --- ВОСКРЕСНЫЙ СУД (/court) ---
@dp.message(Command("court"))
async def cmd_court(message: types.Message):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT nickname, hc, aura FROM users WHERE hc < 0 OR aura < 0")
    debtors = c.fetchall()
    conn.close()

    if not debtors:
        return await message.answer(
            "⚖️ **ВОСКРЕСНЫЙ СУД ТРЕП ХАТЫ:**\n\n"
            "Все бродяги при койнах и с положительной аурой! Должников и опущенных нет. Алхан доволен. 🙏",
            parse_mode="Markdown"
        )

    text = "⚖️🔥 **ВОСКРЕСНЫЙ СУД И КОЛЕСО НАКАЗАНИЙ!** 🔥⚖️\n\nОбнаружены должники или персонажи с отрицательной аурой:\n\n"
    for nick, hc, aura in debtors:
        punish = random.choice(PUNISHMENTS)
        text += (
            f"💀 Бродяга: **{nick}** (Баланс: **{hc:.1f} HC**, Аура: **{aura}**)\n"
            f"🔨 **Приговор суда:** {punish}\n\n"
        )
    text += "*Выполняйте наказания или закрывайте долги через `/claim`!*"
    await message.answer(text, parse_mode="Markdown")

async def main():
    print("🔥 Бот ТРЕП ХАТА v3.0 PRO запущен и готов к работе во всех чатах!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())