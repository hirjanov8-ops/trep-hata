import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from database import DB_NAME, init_db

TOKEN = "8618073795:AAHyzr6DrzlOYeCbHMxertS080KldaBUPqo"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Инициализация БД
init_db()

# --- ПОМОЩНИКИ ---
def get_user(user_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, name, hc, aura FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row

# --- КОМАНДЫ И ОБУЧЕНИЕ ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, name) VALUES (?, ?)", (user_id, name))
    conn.commit()
    conn.close()
    
    # Приветствие с подробным обучением
    text = (
        "🏠 **ДОБРО ПОЖАЛОВАТЬ В ТРЕП ХАТУ!**\n\n"
        "Здесь всё по-пацански: убираешься, готовишь, покупаешь бухло или хавку — кидаешь отчёт в бота. "
        "Пацаны решают: *Правда это или пиздёж*.\n\n"
        "🎮 **ФИШКИ СИСТЕМЫ:**\n"
        "• **ХатаКойны (HC):** Валюта за любые дела (1-5 HC за задачу).\n"
        "• **Кейсы со шмотки:** Открывай кейсы, выбивай шмот на общего перса и редкие ачивки!\n"
        "• **Апгрейд шмоток:** Рискуй шмотом под шансы 10%, 30%, 50%, 75% ради редкого дропа.\n"
        "• **Аура:** Кореша накидывают тебе ауру за поступки. Чем больше ауры, тем ты пизже.\n"
        "• **Воскресный Суд:** Кто в конце недели с минусовым балансом — тот крутит барабан наказаний!\n\n"
        "👇 Жми кнопку ниже, чтобы открыть Mini App «Треп Хата»!"
    )
    
    kb = InlineKeyboardBuilder()
    kb.button(text="🚀 Открыть Треп Хату (Mini App)", web_app=types.WebAppInfo(url="ТВОЙ_URL_MINI_APP"))
    kb.button(text="📖 Как тут всё устроено (FAQ)", callback_data="faq")
    kb.adjust(1)
    
    await message.answer(text, reply_markup=kb.as_markup(), parse_mode="Markdown")

@dp.callback_query(F.data == "faq")
async def callback_faq(callback: types.CallbackQuery):
    faq_text = (
        "📖 **МАНУАЛ ПО ТРЕП ХАТЕ:**\n\n"
        "1️⃣ **Как заработать HC?** Делаешь движ в хате -> создаешь отчёт в боте -> пацаны жмут 'Правда' -> получаешь HC. Если оба сказали 'Пиздёж' -> улетаешь в минус.\n"
        "2️⃣ **Ауры:** Если сожитель замутил лютую тему, жми ему ауру через бота, поднимай его авторитет.\n"
        "3️⃣ **Минус баланс:** Если к концу недели баланс < 0, бот вызывает Воскресный Суд с рандомным наказанием.\n"
        "4️⃣ **Шмотки и Рынок:** Шмот можно продавать за дешман (0.1 HC) или копить на имбовые шмотки за 10 HC."
    )
    await callback.message.answer(faq_text, parse_mode="Markdown")
    await callback.answer()

@dp.message(Command("help_bot"))
async def cmd_help(message: types.Message):
    await message.answer("💡 **Шпаргалка по боту:**\n/start — Главное меню и Mini App\n/top — Доска позора и уважения (Топ Хаты)\n/help_bot — Эта справка", parse_mode="Markdown")

@dp.message(Command("top"))
async def cmd_top(message: types.Message):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT name, hc, aura FROM users ORDER BY hc DESC")
    users = cursor.fetchall()
    conn.close()
    
    text = "🏆 **ДОСКА ПОЧЁТА И ЕБУЧИХ ЛОХОВ (ТОП ХАТЫ):**\n\n"
    for idx, (name, hc, aura) in enumerate(users, 1):
        status = "👑 Батя" if idx == 1 else "💩 Ебучий лох" if hc < 0 else "💪 Житель"
        text += f"{idx}. **{name}** — {hc} HC | Аура: {aura} ✨ | *{status}*\n"
        
    await message.answer(text, parse_mode="Markdown")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())