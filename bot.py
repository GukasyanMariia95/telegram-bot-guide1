print("Старт кода бота")

import logging
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import TOKEN

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

ADMIN_CHAT_ID = 733137079  # Твой числовой ID

kb = ReplyKeyboardMarkup(resize_keyboard=True)
kb.add(KeyboardButton("📘 Что внутри гайда"))
kb.add(KeyboardButton("💰 Купить гайд"))
kb.add(KeyboardButton("❓ Задать вопрос"))

class QuestionState(StatesGroup):
    waiting_for_question = State()

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await message.answer(
        """👋 Привет!
Я — Мария Гукасян, и я верю, что твои курсы не должны зависеть от прогревов, сторис и выгорания.

Ты можешь продавать на автомате — без «впихивания» и ручных переписок.
И всё, что тебе нужно — это правильно выстроенная автоворонка в Telegram.

📘 Этот гайд — твоя первая ступень в сторону системных продаж.

Выбери, что тебя интересует:""",
        reply_markup=kb
    )

@dp.message_handler(lambda msg: msg.text == "📘 Что внутри гайда")
async def guide_info(message: types.Message):
    text = """Что внутри гайда: 

— Простая схема автоворонки для экспертов и новичков
— Примеры сообщений, которые продают
— Подключение Telegram-бота
— Бонус: чек-лист для запуска за 1 день

Ты сможешь запустить свою первую автоворонку сразу после прочтения!"""
    await message.answer(text)

@dp.message_handler(lambda msg: msg.text == "💰 Купить гайд")
async def buy_guide(message: types.Message):
    text = """💸 Стоимость гайда — 490₽
Оплати по следующим реквизитам:

🔹 Номер счёта:
`40817 810 3 0685 0024338`

❗ После оплаты — пришли сюда скриншот или фото чека.
Я проверю и пришлю тебе гайд 😊"""
    await message.answer(text, parse_mode='Markdown')

@dp.message_handler(lambda msg: msg.text == "❓ Задать вопрос")
async def ask_question(message: types.Message):
    await message.answer("Напиши свой вопрос, и я обязательно отвечу тебе.")
    await QuestionState.waiting_for_question.set()

@dp.message_handler(state=QuestionState.waiting_for_question, content_types=types.ContentTypes.TEXT)
async def forward_question(message: types.Message, state: FSMContext):
    user = message.from_user
    question = message.text
    await bot.send_message(ADMIN_CHAT_ID, f"Вопрос от @{user.username or user.id} ({user.full_name}):\n\n{question}")
    await message.answer("Спасибо за вопрос! Я скоро тебе отвечу.")
    await state.finish()

@dp.message_handler(content_types=['photo', 'document'])
async def handle_payment_proof(message: types.Message):
    user = message.from_user
    caption = f"📥 Новый скрин оплаты от @{user.username or user.id}\nИмя: {user.full_name}"

    if message.photo:
        file_id = message.photo[-1].file_id
        await bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=file_id, caption=caption)
    elif message.document:
        await bot.send_document(chat_id=ADMIN_CHAT_ID, document=message.document.file_id, caption=caption)

    await message.answer("✅ Спасибо! Я проверю оплату и пришлю тебе гайд как можно скорее.")

@dp.message_handler(commands=['reply'])
async def admin_reply(message: types.Message):
    if message.chat.id != ADMIN_CHAT_ID:
        return  # Игнорируем, если не админ

    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.reply("Используй команду так:\n/reply <user_id> <текст ответа>")
        return

    try:
        user_id = int(args[1])
    except ValueError:
        await message.reply("Неверный user_id. Это должно быть число.")
        return

    answer_text = args[2]

    try:
        await bot.send_message(user_id, f"Ответ от меня:\n\n{answer_text}")
        await message.reply("Ответ отправлен пользователю.")
    except Exception as e:
        await message.reply(f"Не удалось отправить сообщение: {e}")

@dp.message_handler()
async def echo_all(message: types.Message):
    await message.answer("Я получил сообщение!")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
