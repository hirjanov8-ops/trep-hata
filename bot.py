import asyncio
import json
import random
import sqlite3
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware, Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from database import (
    DB_NAME,
    init_db,
    register_chat,
    get_all_chats,
    ensure_user,
    get_aura_title,
    get_hc_rank,
    generate_claim_code,
    estimate_custom_task_reward,
)

# =========================================================================
# НАСТРОЙКИ (ТВОЙ ТОКЕН И ССЫЛКА С ВЕРСИЕЙ ?v=4 ДЛЯ СБРОСА КЭША ТЕЛЕГРАМА)
# =========================================================================
TOKEN = "8618073795:AAHyzr6DrzlOYeCbHMxertS080KldaBUPqo"
WEBAPP_URL = "https://hirjanov8-ops.github.io/trep-hata/web_app/?v=4"

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


# --- НАСТОЯЩИЙ MIDDLEWARE (НЕ БЛОКИРУЕТ КОМАНДЫ!) ---
class ChatAndUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[types.TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: types.TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, types.Message):
            if event.chat.type in ["group", "supergroup"]:
                register_chat(event.chat.id, event.chat.title, event.chat.type)
            if event.from_user:
                ensure_user(event.from_user.id, event.from_user.username, event.from_user.first_name)
        elif isinstance(event, types.CallbackQuery):
            if event.message and event.message.chat.type in ["group", "supergroup"]:
                register_chat(event.message.chat.id, event.message.chat.title, event.message.chat.type)
            if event.from_user:
                ensure_user(event.from_user.id, event.from_user.username, event.from_user.first_name)
        return await handler(event, data)


dp.message.middleware(ChatAndUserMiddleware())
dp.callback_query.middleware(ChatAndUserMiddleware())


# --- ФУНКЦИЯ РАССЫЛКИ ОПРОСА ВО ВСЕ ЧАТЫ ---
async def create_and_broadcast_poll(user: types.User, task_desc: str, reward: float, aura: int, origin_chat_id: int = None):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "INSERT INTO polls (creator_id, creator_name, task_title, reward, aura_bonus) VALUES (?, ?, ?, ?, ?)",
        (user.id, user.first_name, task_desc, reward, aura)
    )
    poll_id = c.lastrowid
    conn.commit()
    conn.close()

    ikb = InlineKeyboardBuilder()
    ikb.button(text=f"✅ Правда (+{reward:g} HC)", callback_data=f"vote_yes_{poll_id}")
    ikb.button(text="❌ Пиздёж (-3 HC)", callback_data=f"vote_no_{poll_id}")
    ikb.adjust(2)

    poll_text = (
        f"🚨 **ПРОВЕРКА ДЕЛА #{poll_id}** 🚨\n\n"
        f"👤 Заявитель: **{user.first_name}**\n"
        f"📋 Задача: **{task_desc}**\n"
        f"💎 Награда: **+{reward:g} HC** | ✨ **+{aura} Ауры**\n\n"
        f"⚖️ *Статус: 0/2 голосов «Правда» (Сам за себя голосовать не может!)*"
    )

    chats = get_all_chats()
    target_chat_ids = set(ch[0] for ch in chats)
    if origin_chat_id:
        target_chat_ids.add(origin_chat_id)

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    sent_count = 0

    for cid in target_chat_ids:
        try:
            msg = await bot.send_message(cid, poll_text, reply_markup=ikb.as_markup(), parse_mode="Markdown")
            c.execute(
                "INSERT INTO poll_messages (poll_id, chat_id, message_id) VALUES (?, ?, ?)",
                (poll_id, cid, msg.message_id)
            )
            sent_count += 1
        except Exception:
            pass

    conn.commit()
    conn.close()
    return poll_id, sent_count


# --- /start И ГЛАВНОЕ МЕНЮ ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    rkb = ReplyKeyboardBuilder()
    rkb.button(text="🔥 ОТКРЫТЬ ТРЕП ХАТУ (Mini App)", web_app=types.WebAppInfo(url=WEBAPP_URL))
    rkb.button(text="📊 Топ Хаты")
    rkb.button(text="⚖️ Воскресный Суд")
    rkb.button(text="📖 Все фишки бота")
    rkb.adjust(1, 2, 1)

    ikb = InlineKeyboardBuilder()
    ikb.button(text="🚀 Запустить Mini App (Прямо тут)", web_app=types.WebAppInfo(url=WEBAPP_URL))
    ikb.button(text="🧹 Быстро заявить дело в чате", callback_data="quick_claim_menu")
    ikb.adjust(1)

    text = (
        "🏠 **СИСТЕМА «ТРЕП ХАТА v3.5 ULTIMATE» АКТИВИРОВАНА!**\n\n"
        "Здарова, бродяга! Это пульт управления нашей хатой (Саня Жиросан, Карась, Кирилл Карлик Джексон).\n"
        "• 💰 Стартовый баланс: **5.0 HC**\n"
        "• 🕺 Личный манекен у каждого (включая **Фулл Сет Майкла Джексона**, **Голову/Хвост Карася**, **Халат Жиросана Кэмел** и **Трусы Птицы**)\n"
        "• ⚖️ Честная проверка заданий: нужно **ровно 2 голоса «Правда»** от соседей!\n"
        "• 🐓 Уйдёшь по Ауре в минус — станешь **Опущенным** с мухами и наценкой +25% на кейсы!\n\n"
        "👇 **Жми кнопку ниже, чтобы открыть приложение или отправить отчёт о деле!**"
    )
    await message.answer(text, reply_markup=rkb.as_markup(resize_keyboard=True), parse_mode="Markdown")
    await message.answer("Быстрая панель:", reply_markup=ikb.as_markup())


# --- БЫСТРОЕ МЕНЮ ЗАДАНИЙ ПРЯМО В ЧАТЕ ---
@dp.callback_query(F.data == "quick_claim_menu")
async def cb_quick_claim_menu(call: types.CallbackQuery):
    ikb = InlineKeyboardBuilder()
    presets = [
        ("🗑️ Вынес мусор (+1.5 HC)", "qtask_Вынес мусор и бутылки_1.5_8"),
        ("🍽️ Помыл всю посуду (+2 HC)", "qtask_Помыл всю посуду и раковину_2.0_10"),
        ("🍳 Приготовил Омлет Карася (+3 HC)", "qtask_Приготовил похавать на всю хату_3.0_15"),
        ("🧹 Помыл полы / Пропылесосил (+3.5 HC)", "qtask_Пропылесосил и помыл полы_3.5_18"),
        ("🚽 Надраил толчок и плиту (+4.5 HC)", "qtask_Надраил толчок ванну и плиту_4.5_22"),
        ("🦌 Забашлял за Ягерь / Виски (+5 HC)", "qtask_Забашлял за бухло и энергетики_5.0_25"),
    ]
    for label, cb_data in presets:
        ikb.button(text=label, callback_data=cb_data)
    ikb.adjust(1)
    await call.message.answer(
        f"⚡ **{call.from_user.first_name}**, выбери выполненное дело (или напиши своё через `/claim текст`):",
        reply_markup=ikb.as_markup(),
        parse_mode="Markdown"
    )
    await call.answer()


@dp.callback_query(F.data.startswith("qtask_"))
async def cb_qtask_create(call: types.CallbackQuery):
    _, title, hc_s, aura_s = call.data.split("_")
    reward = float(hc_s)
    aura = int(aura_s)
    poll_id, sent_cnt = await create_and_broadcast_poll(
        call.from_user, title, reward, aura, origin_chat_id=call.message.chat.id
    )
    await call.answer(f"Опрос #{poll_id} разослан в чаты ({sent_cnt} шт.)!", show_alert=True)


# --- СПРАВКА /help_bot ---
@dp.message(Command("help_bot"))
@dp.message(F.text == "📖 Все фишки бота")
async def cmd_help_bot(message: types.Message):
    text = (
        "📖 **ПОЛНЫЙ МАНУАЛ ТРЕП ХАТЫ v3.5:**\n\n"
        "1️⃣ **Опросы «Правда или Пиздёж» во всех чатах (Без халявы):**\n"
        "Когда ты жмёшь задание в Mini App или пишешь `/claim Помыл плиту`, бот рассылает опрос **во все чаты хаты**. "
        "Чтобы задание засчиталось, нужно **ровно 2 голоса «Правда»** от соседей (сам за себя проголосовать не сможешь). "
        "После 2 голосов бот начисляет койны в БД и выдаёт защищённый **Пин-код** для Mini App!\n\n"
        "2️⃣ **Система Ауры и Опущенных:**\n"
        "• Ответь (reply) командой `/aura` на сообщение кента — накинешь ему **+15 Ауры**.\n"
        "• Ответь командой `/shame` — снимешь **-20 Ауры**.\n"
        "• Если Аура падает `< 0`, чел становится **🐓 Опущенным** (вокруг манекена летают мухи, кейсы дороже на 25%, апгрейд режется).\n\n"
        "3️⃣ **Бухгалтерия и Сплит чеков (`/split`):**\n"
        "Напиши `/split 1800 Продукты и яйца` — бот поделит чек на троих (по 600 ₽ с каждого соседа), запишет в базу расходов и даст тебе **+2 HC**.\n\n"
        "4️⃣ **Топы и Воскресный Суд:**\n"
        "• `/top` — Живой рейтинг богачей, работяг и опущенных.\n"
        "• `/court` — Барабан наказаний для всех, у кого баланс `< 0` или Аура `< 0`!"
    )
    await message.answer(text, parse_mode="Markdown")


# --- СОЗДАНИЕ СВОЕГО ЗАДАНИЯ ЧЕРЕЗ /claim ---
@dp.message(Command("claim"))
async def cmd_claim(message: types.Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return await message.answer(
            "✍️ **Как заявить своё задание в чате:**\n"
            "Напиши: `/claim Сгонял ночью за шавухой и вынес мусор`\n"
            "ИИ-оценщик сам рассчитает награду (от 1 до 5 HC) и отправит опрос во все чаты на 2 голоса!",
            parse_mode="Markdown"
        )

    task_desc = parts[1].strip()
    reward, aura = estimate_custom_task_reward(task_desc)
    poll_id, sent_count = await create_and_broadcast_poll(
        message.from_user, task_desc, reward, aura, origin_chat_id=message.chat.id
    )
    if sent_count == 0:
        await message.answer("Добавь бота в общий чат хаты и напиши там любое сообщение, чтобы он запомнил беседу!")


# --- ОБРАБОТКА ГОЛОСОВАНИЯ (СТРОГО 2 ГОЛОСА + ЗАЩИТА ОТ САМОЛАЙКА) ---
@dp.callback_query(F.data.startswith("vote_"))
async def cb_vote(call: types.CallbackQuery):
    _, decision, poll_id_str = call.data.split("_")
    poll_id = int(poll_id_str)
    voter = call.from_user

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "SELECT creator_id, creator_name, task_title, reward, aura_bonus, yes_voters, yes_names, no_voters, status FROM polls WHERE poll_id = ?",
        (poll_id,)
    )
    row = c.fetchone()

    if not row:
        conn.close()
        return await call.answer("Опрос не найден!", show_alert=True)

    creator_id, creator_name, task_title, reward, aura_bonus, yes_voters_str, yes_names_str, no_voters_str, status = row

    if status != "pending":
        conn.close()
        return await call.answer("Этот опрос уже закрыт!", show_alert=True)

    # ЖЕЛЕЗНАЯ ЗАЩИТА: создатель не может голосовать сам за себя!
    if voter.id == creator_id:
        conn.close()
        return await call.answer("Хитрожопый? Сам за себя голосовать нельзя! Жди голоса Карася и Кирилла!", show_alert=True)

    yes_list = [int(x) for x in yes_voters_str.split(",") if x]
    yes_names = [x for x in (yes_names_str or "").split(",") if x]
    no_list = [int(x) for x in no_voters_str.split(",") if x]

    if voter.id in yes_list or voter.id in no_list:
        conn.close()
        return await call.answer("Ты уже голосовал в этом опросе!", show_alert=True)

    if decision == "yes":
        yes_list.append(voter.id)
        yes_names.append(voter.first_name)
    else:
        no_list.append(voter.id)

    new_yes_str = ",".join(map(str, yes_list))
    new_names_str = ",".join(yes_names)
    new_no_str = ",".join(map(str, no_list))

    # Получаем все сообщения этого опроса во всех чатах
    c.execute("SELECT chat_id, message_id FROM poll_messages WHERE poll_id = ?", (poll_id,))
    msg_rows = c.fetchall()

    # СЦЕНАРИЙ 1: Поймали на пиздеже (достаточно 1 голоса против от соседа или 2)
    if len(no_list) >= 1:
        c.execute("UPDATE polls SET status = 'rejected', no_voters = ? WHERE poll_id = ?", (new_no_str, poll_id))
        c.execute(
            "UPDATE users SET hc = hc - 3.0, aura = aura - 20, lies_count = lies_count + 1 WHERE user_id = ?",
            (creator_id,)
        )
        conn.commit()
        conn.close()

        result_text = (
            f"❌ **ПОЙМАН НА ПИЗДЕЖЕ (#{poll_id})!** 🚨\n\n"
            f"🤡 Скаммер: **{creator_name}** ({task_title})\n"
            f"🕵️‍♂️ Разоблачил: **{voter.first_name}**\n"
            f"📉 Штраф: **-3.0 HC** и **-20 Ауры**!"
        )
        for cid, mid in msg_rows:
            try:
                await bot.edit_message_text(result_text, chat_id=cid, message_id=mid, parse_mode="Markdown")
            except Exception:
                pass
        return await call.answer("Скаммер наказан!")

    # СЦЕНАРИЙ 2: Набрано РОВНО 2 ГОЛОСА «Правда»!
    if len(yes_list) >= 2:
        claim_code = generate_claim_code(reward, aura_bonus)
        c.execute(
            "UPDATE polls SET status = 'approved', yes_voters = ?, yes_names = ?, claim_code = ? WHERE poll_id = ?",
            (new_yes_str, new_names_str, claim_code, poll_id)
        )
        c.execute(
            "UPDATE users SET hc = hc + ?, aura = aura + ?, tasks_done = tasks_done + 1 WHERE user_id = ?",
            (reward, aura_bonus, creator_id)
        )
        conn.commit()
        conn.close()

        result_text = (
            f"✅ **ДЕЛО ОДОБРЕНО ПАЦАНАМИ (2/2 ГОЛОСА) #{poll_id}!**\n\n"
            f"👤 Красавчик: **{creator_name}**\n"
            f"📋 Сделал: **{task_title}**\n"
            f"🤝 Подтвердили: **{', '.join(yes_names)}**\n"
            f"💎 Награда: **+{reward:g} HC** и **+{aura_bonus} Ауры**!\n\n"
            f"🔑 **Пин-код для Mini App:** `{claim_code}`\n"
            f"*(Скопируй код и вставь во вкладке «Дела» в приложении!)*"
        )
        for cid, mid in msg_rows:
            try:
                await bot.edit_message_text(result_text, chat_id=cid, message_id=mid, parse_mode="Markdown")
            except Exception:
                pass

        # Дополнительно шлём Пин-код в личку создателю, чтобы не потерял
        try:
            await bot.send_message(
                creator_id,
                f"🎉 Твоё задание **«{task_title}»** набрало 2/2 голосов!\n"
                f"🔑 Твой Пин-код на **+{reward:g} HC и +{aura_bonus} Ауры**:\n`{claim_code}`",
                parse_mode="Markdown"
            )
        except Exception:
            pass

        return await call.answer("2/2 голоса! Выдан Пин-код!")

    # СЦЕНАРИЙ 3: Пока только 1/2 голосов — обновляем текст опроса во всех чатах!
    c.execute(
        "UPDATE polls SET yes_voters = ?, yes_names = ?, no_voters = ? WHERE poll_id = ?",
        (new_yes_str, new_names_str, new_no_str, poll_id)
    )
    conn.commit()
    conn.close()

    ikb = InlineKeyboardBuilder()
    ikb.button(text=f"✅ Правда ({len(yes_list)}/2)", callback_data=f"vote_yes_{poll_id}")
    ikb.button(text="❌ Пиздёж (-3 HC)", callback_data=f"vote_no_{poll_id}")
    ikb.adjust(2)

    updated_text = (
        f"🚨 **ПРОВЕРКА ДЕЛА #{poll_id}** 🚨\n\n"
        f"👤 Заявитель: **{creator_name}**\n"
        f"📋 Задача: **{task_title}**\n"
        f"💎 Награда: **+{reward:g} HC** | ✨ **+{aura_bonus} Ауры**\n\n"
        f"✅ Уже подтвердил (1/2): **{', '.join(yes_names)}**\n"
        f"⏳ *Ждём 2-й голос от второго соседа!*"
    )
    for cid, mid in msg_rows:
        try:
            await bot.edit_message_text(updated_text, chat_id=cid, message_id=mid, reply_markup=ikb.as_markup(), parse_mode="Markdown")
        except Exception:
            pass

    await call.answer("1/2 голос принят! Ждём второго соседа!")


# --- ПРИЁМ ДАННЫХ ИЗ MINI APP (СИНХРОНИЗАЦИЯ + ОПРОСЫ ВО ВСЕ ЧАТЫ + ЧЕКИ) ---
@dp.message(F.web_app_data)
async def handle_webapp_data(message: types.Message):
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
        aura = int(data.get("aura", 10))
        cases_opened = int(data.get("cases_opened", 0))
        inv_count = int(data.get("inv_count", 0))
        outfit = data.get("outfit", {})

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute(
            """UPDATE users 
               SET nickname = ?, role = ?, hc = ?, aura = ?, cases_opened = ?, inventory_count = ?, equipped_json = ? 
               WHERE user_id = ?""",
            (nickname, role, hc, aura, cases_opened, inv_count, json.dumps(outfit, ensure_ascii=False), user.id)
        )
        conn.commit()
        conn.close()

        aura_title = get_aura_title(aura)
        hc_rank = get_hc_rank(hc, aura)
        outfit_lines = "\n".join([f"• {k}: *{v}*" for k, v in outfit.items()]) if outfit else "• Голый манекен"

        text = (
            f"🧍 **КАРТОЧКА ПЕРСА ИЗ MINI APP:**\n\n"
            f"👤 Ник: **{nickname}** ({role})\n"
            f"💰 Баланс: **{hc:.1f} HC** ({hc_rank})\n"
            f"✨ Аура: **{aura}** ({aura_title})\n"
            f"📦 Открыто кейсов: **{cases_opened}** | 🎒 Шмоток: **{inv_count}**\n\n"
            f"👕 **Надето на манекене:**\n{outfit_lines}"
        )
        await message.answer(text, parse_mode="Markdown")

    elif action == "create_task_poll":
        title = data.get("title", "Дело по хате")
        reward = float(data.get("reward", 2.0))
        aura = int(data.get("aura", 10))
        poll_id, sent_cnt = await create_and_broadcast_poll(
            user, title, reward, aura, origin_chat_id=message.chat.id
        )
        await message.answer(
            f"📢 **Опрос #{poll_id} разослан во все чаты хаты ({sent_cnt} шт.)!**\n"
            f"Как только 2 соседа нажмут **«✅ Правда»**, я пришлю тебе сюда Пин-код на **+{reward:g} HC и +{aura} Ауры**!",
            parse_mode="Markdown"
        )

    elif action == "add_expense":
        payer = data.get("payer", user.first_name)
        title = data.get("title", "Общая покупка")
        amount = float(data.get("amount", 0))
        per_person = round(amount / 3, 2)

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute(
            "INSERT INTO expenses (payer_id, payer_name, amount, description) VALUES (?, ?, ?, ?)",
            (user.id, payer, amount, title)
        )
        conn.commit()
        conn.close()

        # Рассылаем уведомление о чеке во все чаты
        chats = get_all_chats()
        exp_text = (
            f"🧾 **НОВЫЙ ЧЕК ИЗ MINI APP!**\n\n"
            f"💳 Заплатил: **{payer}**\n"
            f"🛒 Покупка: **{title}**\n"
            f"💰 Сумма: **{amount:g} ₽**\n"
            f"➗ **С каждого из остальных двоих по: {per_person:g} ₽**"
        )
        for cid, _, _ in chats:
            try:
                await bot.send_message(cid, exp_text, parse_mode="Markdown")
            except Exception:
                pass
        await message.answer(exp_text, parse_mode="Markdown")


# --- СИСТЕМА АУРЫ И ОПУЩЕННЫХ (/aura И /shame) ---
@dp.message(Command("aura"))
async def cmd_aura(message: types.Message):
    if not message.reply_to_message:
        return await message.answer(
            "☝️ Ответь (reply) командой `/aura` на сообщение кента, чтобы накинуть ему **+15 Ауры**!",
            parse_mode="Markdown"
        )

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
    code = generate_claim_code(0.5, 15)
    await message.answer(
        f"✨ **{message.from_user.first_name}** выразил мощный респект **{target.first_name}**!\n"
        f"📈 Аура в чате: **{new_aura} ✨** ({status_title})\n"
        f"🔑 Код синхронизации (+15 Ауры в Mini App): `{code}`",
        parse_mode="Markdown"
    )


@dp.message(Command("shame"))
async def cmd_shame(message: types.Message):
    if not message.reply_to_message:
        return await message.answer("☝️ Ответь (reply) командой `/shame` на сообщение того, кто ведёт себя как Пень или Птица!")

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
    warning = "\n🐓 **ВНИМАНИЕ: Чел улетел в минус по ауре и официально стал ОПУЩЕННЫМ!**" if new_aura < 0 else ""
    await message.answer(
        f"💩 **{message.from_user.first_name}** опустил ауру **{target.first_name}** на **-20**!\n"
        f"📉 Текущая аура: **{new_aura} ✨** ({status_title}){warning}",
        parse_mode="Markdown"
    )


# --- КАЛЬКУЛЯТОР СПЛИТА ЧЕКОВ (/split) ---
@dp.message(Command("split"))
async def cmd_split(message: types.Message):
    parts = message.text.split(maxsplit=2)
    if len(parts) < 2:
        return await message.answer(
            "🧮 **Калькулятор чеков Треп Хаты:**\n"
            "Пиши: `/split 1800 Закупка продуктов и яиц на омлет`\n"
            "Бот разделит сумму на троих и выдаст тебе Пин-код на **+2.0 HC**!",
            parse_mode="Markdown"
        )

    try:
        amount = float(parts[1])
    except ValueError:
        return await message.answer("Сумма должна быть числом! Пример: `/split 1500 Пиво и хлеб`")

    desc = parts[2] if len(parts) > 2 else "Общая закупка на хату"
    per_person = round(amount / 3, 2)

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "INSERT INTO expenses (payer_id, payer_name, amount, description) VALUES (?, ?, ?, ?)",
        (message.from_user.id, message.from_user.first_name, amount, desc)
    )
    c.execute("UPDATE users SET hc = hc + 2.0, aura = aura + 10 WHERE user_id = ?", (message.from_user.id,))
    conn.commit()
    conn.close()

    bonus_code = generate_claim_code(2.0, 10)
    await message.answer(
        f"🧾 **БУХГАЛТЕРИЯ ТРЕП ХАТЫ (Сплит чека)**\n\n"
        f"💳 Оплатил: **{message.from_user.first_name}**\n"
        f"🛒 Покупка: **{desc}**\n"
        f"💰 Общая сумма: **{amount:g} ₽**\n"
        f"➗ **С каждого из двоих соседей по: {per_person:g} ₽**\n\n"
        f"🎁 За суету с покупкой **{message.from_user.first_name}** получает **+2.0 HC** и **+10 Ауры**!\n"
        f"🔑 Пин-код для Mini App: `{bonus_code}`",
        parse_mode="Markdown"
    )


# --- ТОП ХАТЫ ---
@dp.message(Command("top"))
@dp.message(F.text == "📊 Топ Хаты")
async def cmd_top(message: types.Message):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "SELECT nickname, role, hc, aura, tasks_done, lies_count, cases_opened, inventory_count FROM users ORDER BY hc DESC, aura DESC"
    )
    rows = c.fetchall()
    conn.close()

    text = "🏆 **ОФИЦИАЛЬНЫЙ РЕЙТИНГ ТРЕП ХАТЫ:**\n\n"
    for idx, (nick, role, hc, aura, tasks, lies, cases, inv_cnt) in enumerate(rows, 1):
        medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else "🔸"
        hc_rank = get_hc_rank(hc, aura)
        aura_title = get_aura_title(aura)
        text += (
            f"{medal} **{idx}. {nick}** ({role})\n"
            f"   💰 Баланс: **{hc:.1f} HC** | ✨ Аура: **{aura}**\n"
            f"   🎖️ Ранг: *{hc_rank}* | *{aura_title}*\n"
            f"   ✅ Дел: {tasks} | 📦 Кейсов: {cases} | 🎒 Шмоток: {inv_cnt} | 🤡 Пиздежа: {lies}\n\n"
        )
    await message.answer(text, parse_mode="Markdown")


# --- ВОСКРЕСНЫЙ СУД (/court) ---
@dp.message(Command("court"))
@dp.message(F.text == "⚖️ Воскресный Суд")
async def cmd_court(message: types.Message):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT nickname, hc, aura FROM users WHERE hc < 0 OR aura < 0")
    debtors = c.fetchall()
    conn.close()

    if not debtors:
        return await message.answer(
            "⚖️ **ВОСКРЕСНЫЙ СУД ТРЕП ХАТЫ:**\n\n"
            "Проверил базу — все пацаны при койнах и с ровной аурой! Должников и опущенных сегодня нет. Алхан доволен. 🙏",
            parse_mode="Markdown"
        )

    text = "⚖️🔥 **ВОСКРЕСНЫЙ СУД И КОЛЕСО НАКАЗАНИЙ!** 🔥⚖️\n\nОбнаружены должники или опущенные по ауре:\n\n"
    for nick, hc, aura in debtors:
        punish = random.choice(PUNISHMENTS)
        reason = "Опущенный по Ауре 🐓" if aura < 0 else "Должник по Койнам 💩"
        text += (
            f"💀 Подсудимый: **{nick}** ({reason}: **{hc:.1f} HC**, Аура **{aura}**)\n"
            f"🔨 **Приговор барабана:** {punish}\n\n"
        )
    text += "*Чтобы снять позор, выполни приговор и отправь отчёт через `/claim`!*"
    await message.answer(text, parse_mode="Markdown")


async def main():
    print("🔥 Бот ТРЕП ХАТА v3.5 ULTIMATE успешно запущен! Все команды работают!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())