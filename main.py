from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = "8474431519:AAG07_LjJlq9ExZ2tigtYpip6AD_RO5Fk-0"
CHANNEL_ID = "@Garant801" 

bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

# Главное меню
main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.row("🎟 Приобрести ключ", "💬 Отзывы")
main_kb.row("📌 Частые вопросы", "🛠 Тех поддержка")
main_kb.row("🌐 Создать скам ссылку",)
main_kb.row("🔑 Ввести ключ")

# Меню после ошибки при создании ссылки
error_kb = ReplyKeyboardMarkup(resize_keyboard=True)
error_kb.row("🎟 Приобрести ключ", "💬 Отзывы")
error_kb.row("⬅️ Назад")

@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📢 Канал 1", url=f"https://t.me/{CHANNEL_ID.replace('@','')}"))
    kb.add(InlineKeyboardButton("✅ Подписался", callback_data="check_sub"))
    await message.answer(
        "⚠️ <b>Пожалуйста, подпишитесь на канал для завершения регистрации.</b>",
        reply_markup=kb
    )

@dp.callback_query_handler(lambda c: c.data == "check_sub")
async def check_subscription(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        if member.status in ["member", "administrator", "creator"]:
            await callback.message.answer(
                "👋 <b>Здарова!</b>\n\n"
                "Я являюсь детищем чувака с ником <b>FuryLink♥️</b>\n"
                "Облегчу тебе жизнь👌🏻 Удачи!\n\n"
                "➡️ Выбери пункт:",
                reply_markup=main_kb
            )
        else:
            await callback.answer("❌ Ошибка! Вы не подписались.", show_alert=True)
    except:
        await callback.answer("⚠️ Ошибка проверки подписки.", show_alert=True)

# --- Приобрести ключ ---
@dp.message_handler(lambda m: m.text == "🎟 Приобрести ключ")
async def buy_key(message: types.Message):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("💳 Купить", url="https://t.me/Garant8010"))
    kb.add(InlineKeyboardButton("⬅️ Назад", callback_data="back"))
    await message.answer(
        "🎟 <b>После оплаты Вам станет доступно:</b>\n\n"
        "- 🌐 Создание скам ссылки\n"
        "- 🎮 Приложение на IOS, android и BlueStacks\n"
        "- 🔓 Получение токена",
        reply_markup=kb
    )

# --- Отзывы ---
@dp.message_handler(lambda m: m.text == "💬 Отзывы")
async def reviews(message: types.Message):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("⬅️ Назад", callback_data="back"))
    await message.answer("💬 <b>Наши отзывы:</b>\nhttps://t.me/Garant801", reply_markup=kb)

# --- Частые вопросы ---
@dp.message_handler(lambda m: m.text == "📌 Частые вопросы")
async def faq(message: types.Message):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("⬅️ Назад", callback_data="back"))
    await message.answer(
        "Частые вопросы📌\n\n"
        "1. Что я получу после оплаты❓\n"
        "- После оплаты вы получаете два файла (Ipa, Apk)\n"
        "Ipa на iOS, Apk на Android, видео-инструкция как установить приложение и пользоваться им, "
        "а также сам ключ для активации премиума в боте и создания ссылок📎\n\n"
        "2. У меня айфон, смогу ли я установить приложение для токена❓\n"
        "- ДА! Это очень просто, никакой Скарлет или подобные приложения не понадобятся 👍\n\n"
        "3. Что даёт премиум в боте❓\n"
        "- Вы получаете доступ к созданию скам ссылок и получению токена от аккаунта стандофф 🌐\n\n"
        "4. Банят ли за это в стандоффе❓\n"
        "- НЕТ! Бан за то, что вы создаете скам ссылки или переводите себе голду на аккаунт не даётся ♥️\n\n"
        "5. Где можно посмотреть цены❓\n"
        "- Цены находятся в боте, в разделе «Ключ💳»\n\n"
        "6. Я оплатил и мне дали какой-то ключ, что это❓\n"
        "- После оплаты вы получаете код, который нужно ввести в раздел «Ввести ключ🔑»\n\n"
        "7. Я хочу купить, но вдруг скоро обнова, как быть❓\n"
        "- После оплаты вы попадаете в список покупателей и если выйдет обновление, "
        "то вы получите новое приложение БЕСПЛАТНО ♥️\n\n"
        "8. Я увидел ключ активации в видео-ролике, но он не работает, что делать❓\n"
        "- Все ключи активации одноразовые. Бесплатные ключи не выдаются. "
        "Чтобы приобрести свой ключ, нажмите в боте главное меню > Ключ 🎟️\n\n"
        "9. В день вы можете создавать до 10 скам ссылок. 1 ссылка = 1 мамонт 👾\n\n"
        "10. После оплаты вы получаете приложение для токена и ключ для бота 🔓\n\n"
        "11. В случае возникновения трудностей вы можете обратиться в тех. поддержку ⚙️\n\n"
        "12. Подписки на 1 час или на 1 день не продаются ❗️",
        reply_markup=kb
    )

# --- Тех поддержка ---
@dp.message_handler(lambda m: m.text == "🛠 Тех поддержка")
async def support(message: types.Message):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("⬅️ Назад", callback_data="back"))
    await message.answer("🛠 <b>Тех. поддержка:</b> @Garant8010", reply_markup=kb)

# --- Создать скам ссылку ---
@dp.message_handler(lambda m: m.text == "🌐 Создать скам ссылку")
async def scam_link(message: types.Message):
    await message.answer(
        "🚫 <b>Ошибка создания скам ссылки</b>\n\n"
        "У вас отсутствует подписка, для её активации необходимо приобрести ключ 🔑\n\n"
        "🌐 Создание скам ссылки станет доступно только после активации подписки ♥️",
        reply_markup=error_kb
    )

# --- Ввести ключ ---
BACK_TEXT = "⬅️ Назад"
user_states = {}  # user_id -> "awaiting_key" | None

@dp.message_handler(lambda m: m.text == "🔑 Ввести ключ")
async def enter_key(message: types.Message):
    user_states[message.from_user.id] = "awaiting_key"
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(BACK_TEXT)
    await message.answer("Введите ключ для активации подписки в чат 👇", reply_markup=kb)

@dp.message_handler(lambda m: user_states.get(m.from_user.id) == "awaiting_key")
async def check_key(message: types.Message):
    # 1) если пользователь нажал Назад — выходим из режима ввода ключа
    if message.text == BACK_TEXT:
        user_states[message.from_user.id] = None
        await message.answer("⬅️ Вы вернулись в главное меню", reply_markup=main_kb)
        return

    # 2) иначе это попытка ввести ключ
    CORRECT_KEY = "SECRET123"  # поменяйте на свой
    if message.text.strip() == CORRECT_KEY:
        user_states[message.from_user.id] = None
        await message.answer("✅ Подписка успешно активирована!", reply_markup=main_kb)
    else:
        await message.answer("❌ Введен неверный код")
        
# --- Назад ---
@dp.message_handler(lambda m: m.text == "⬅️ Назад")
async def back_reply(message: types.Message):
    await message.answer("⬅️ Вы вернулись в главное меню", reply_markup=main_kb)

@dp.callback_query_handler(lambda c: c.data == "back")
async def back_menu(callback: types.CallbackQuery):
    await callback.message.answer("⬅️ Вы вернулись в главное меню", reply_markup=main_kb)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
