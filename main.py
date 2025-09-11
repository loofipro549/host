import os
import re
import json
import random
import string
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

TOKEN = "8224640828:AAGOIewXNEk4G1vEcitZisdGNsicLSlXwuE"
DATA_FILE = "bot_data.json"

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        DATA = json.load(f)
else:
    DATA = {"users": {}, "deals": {}}
ADMIN_IDS = DATA.get("admins", [1802110243, 5142424997]) # можно изменить

def save_admins():
    DATA["admins"] = ADMIN_IDS
    save_data()

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(DATA, f, ensure_ascii=False, indent=2)
def get_lil_photo_path():
    folder = "lil"
    if not os.path.isdir(folder):
        return None
    for fn in os.listdir(folder):
        if fn.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            return os.path.join(folder, fn)
    return None

PHOTO_PATH = get_lil_photo_path()


async def send_photo_with_caption(chat_id, caption, reply_markup=None):
    """Send photo (from lil) with caption. If photo missing, send text instead."""
    if PHOTO_PATH and os.path.exists(PHOTO_PATH):
        with open(PHOTO_PATH, "rb") as photo:
            return await bot.send_photo(
                chat_id,
                photo=photo,
                caption=caption,
                reply_markup=reply_markup
            )
    else:
        return await bot.send_message(
            chat_id,
            caption,
            reply_markup=reply_markup
        )

def main_menu_kb(user_id):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("🪙 Добавить/изменить кошелёк", callback_data="wallets"),
        InlineKeyboardButton("📄 Создать сделку", callback_data="create_deal"),
    )
    kb.add(
        InlineKeyboardButton("📎 Реферальная ссылка", callback_data="referral"),
        InlineKeyboardButton("🌐 Сменить язык", callback_data="lang"),
    )
    kb.add(InlineKeyboardButton("📞 Поддержка", url="https://forms.gle/4kN2r57SJiPrxBjf9"))
    return kb


def wallets_kb(user_id):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("💳 Сбербанк", callback_data="pay_sber"),
        InlineKeyboardButton("💳 Тинькофф", callback_data="pay_tink"),
        InlineKeyboardButton("💳 Другая карта", callback_data="pay_other"),
        InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_menu")
    )
    return kb


def back_menu_kb():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🔙 Вернутся в меню", callback_data="back_menu"))
    return kb


def ton_back_kb():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🔙 Вернутся в меню", callback_data="wallets"))
    return kb

def is_valid_ton(addr: str) -> bool:
    addr = addr.strip()
    return (addr.startswith("EQ") or addr.startswith("UQ")) and len(addr) >= 10


def is_valid_sbp(phone: str) -> bool:
    return bool(re.match(r'^\+7\(\d{3}\)\d{3}-\d{2}-\d{2}$', phone.strip()))


def is_valid_card(card: str) -> bool:
    digits = re.sub(r"\D", "", card)
    return digits.isdigit() and len(digits) == 16
USER_STATE = {}


def set_state(user_id, state):
    USER_STATE[str(user_id)] = state


def get_state(user_id):
    return USER_STATE.get(str(user_id))


def clear_state(user_id):
    USER_STATE.pop(str(user_id), None)

def ensure_user(user: types.User):
    uid = str(user.id)
    if uid not in DATA["users"]:
        DATA["users"][uid] = {
            "id": user.id,
            "username": user.username or f"{user.first_name}",
            "wallets": {},
            "language": "ru",
            "balance": 0.0,
            "referrals": 0
        }
        save_data()
    return DATA["users"][uid]

def gen_deal_id(n=10):
    return "d" + ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(n))
@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    args = message.get_args() or ""
    user = ensure_user(message.from_user)
    if args.startswith("ref=") or args.startswith("ref"):
        ref = args.split("=", 1)[1] if "=" in args else args[3:]
        try:
            ref_id = str(int(ref))
            if ref_id != str(user["id"]):
                if user.get("balance", 0) == 0 and user.get("referrals", 0) == 0:
                    user["balance"] = user.get("balance", 0) + 1.0
                    DATA["users"].setdefault(ref_id, {}).setdefault("referrals", 0)
                    if ref_id in DATA["users"]:
                        DATA["users"][ref_id]["referrals"] = DATA["users"][ref_id].get("referrals", 0) + 1
                save_data()
        except Exception:
            pass

    if args.startswith("deal_") or args.startswith("d"):
        deal_id = args
        deal = DATA["deals"].get(deal_id)
        if deal:
            deal['buyer_id'] = str(message.from_user.id)
            deal['buyer_username'] = message.from_user.username or message.from_user.first_name

            deal.setdefault('seller_success', random.randint(3, 160))
            save_data()

            caption = (
                f"<b>💳 Информация о сделке #{deal_id}</b>\n\n"
                f"<b>👤 Вы покупатель</b> в сделке.\n"
                f"<b>📌 Продавец:</b> @{deal['seller_username']} ({deal['seller_id']})\n"
                f"• Успешные сделки: {deal.get('seller_success', 0)}\n\n"
                f"• <b>Вы покупаете:</b> {deal['description']}\n\n"
                f"🏦 Адрес для оплаты: {deal['pay_address']}\n\n"
                f"<b>💰 Сумма:</b> {deal['amount']} {deal['currency']}\n\n"
                f"📝 Комментарий к платежу (мемо): {deal_id}\n\n"
                f"⚠️ Пожалуйста, убедитесь в правильности данных перед оплатой. Комментарий обязателен!"
            )
            kb = InlineKeyboardMarkup(row_width=1)
            kb.add(InlineKeyboardButton("🔗 Открыть в Toonkeper", url="https://tonkeeper.com/"))
            kb.add(InlineKeyboardButton("❌ Выйти из сделки", callback_data=f"exitdeal_{deal_id}"))

            if message.from_user.id in ADMIN_IDS:
                kb.add(InlineKeyboardButton("✅ Подтвердить оплату", callback_data=f"confirm_payment_{deal_id}"))

            await send_photo_with_caption(message.chat.id, caption, reply_markup=kb)

            try:
                seller_chat = int(deal['seller_id'])
                await send_photo_with_caption(
                    seller_chat,
                    f"👤 Пользователь @{deal['buyer_username']} ({deal['buyer_id']}) присоединился к сделке #{deal_id}\n"
                    f"• Успешные сделки: {deal.get('seller_success', 0)}\n\n"
                    f"⚠️ Проверьте, что это тот же пользователь, с которым вы вели диалог ранее!\n"
                    f"Не переводите подарок до получения подтверждения оплаты в этом чате!"
                )
            except Exception:
                pass

            return

    caption = (
        "<b>Добро пожаловать в ELF OTC – надёжный P2P-гарант</b>\n\n"
        "<b>💼 Покупайте и продавайте всё, что угодно – безопасно!</b>\n"
        "От Telegram-подарков и NFT до токенов и фиата – сделки проходят легко и без риска.\n\n"
        "🔹 Удобное управление кошельками\n"
        "🔹 Реферальная система\n\n"
        "<b>📖 Как пользоваться?</b>\n"
        "Ознакомьтесь с инструкцией — https://telegra.ph/Podrobnyj-gajd-po-ispolzovaniyu-GiftElfRobot-04-25\n\n"
        "Выберите нужный раздел ниже:\n"
    )
    kb = main_menu_kb(message.from_user.id)
    await send_photo_with_caption(message.chat.id, caption, reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data == "wallets")
async def cb_wallets(callback_query: types.CallbackQuery):
    user = ensure_user(callback_query.from_user)
    cur = user.get("wallets") or {}
    if cur:
        parts = []
        if "type" in cur:
            if cur["type"] == "STARS":
                parts.append("Выбрана оплата в STARS")
            elif cur["type"] == "card":
                num = cur.get("card_number", "")
                country = cur.get("country", "")
                parts.append(f"{num} | {country}_CARD")
            elif cur["type"] == "ton":
                parts.append(f"TON: {cur.get('ton')}" )
            elif cur["type"] == "sbp":
                parts.append(f"СБП: {cur.get('sbp')}" )
        caption = f"<b>💼Ваш текущий кошелек:</b>\n" + "\n".join(parts) + "\n\nВы можете изменить способ оплаты ниже:"
    else:
        caption = "<b>💼Добавьте ваш способ оплаты:</b>\n\nПожалуйста, выберите тип кошелька ниже:"

    kb = wallets_kb(callback_query.from_user.id)
    await send_photo_with_caption(callback_query.from_user.id, caption, reply_markup=kb)
    await callback_query.answer()


@dp.callback_query_handler(lambda c: c.data == "back_menu")
async def cb_back_menu(c: types.CallbackQuery):
    caption = (
        "<b>Добро пожаловать в ELF OTC – надёжный P2P-гарант</b>\n\n"
        "Выберите нужный раздел ниже:\n"
    )
    kb = main_menu_kb(c.from_user.id)
    await send_photo_with_caption(c.from_user.id, caption, reply_markup=kb)
    await c.answer()


@dp.callback_query_handler(lambda c: c.data == "add_ton")
async def cb_add_ton(c: types.CallbackQuery):
    await send_photo_with_caption(c.from_user.id, "<b>💎 Добавление TON-кошелька</b>\n\nПожалуйста, введите ваш TON адрес", reply_markup=ton_back_kb())
    set_state(c.from_user.id, "adding_ton")
    await c.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("pay_"))
async def cb_pay_method(c: types.CallbackQuery):
    method = c.data.split("_")[1]
    await send_photo_with_caption(c.from_user.id, f"Введите номер карты для {method.upper()} (16 цифр):", reply_markup=back_menu_kb())
    set_state(c.from_user.id, f"adding_card_{method}")
    await c.answer()

@dp.callback_query_handler(lambda c: c.data == "add_sbp")
async def cb_add_sbp(c: types.CallbackQuery):
    await send_photo_with_caption(c.from_user.id, "<b>📱 Добавление СБП</b>\n\nПожалуйста, введите номер телефона в формате: <b>+7(XXX)XXX-XX-XX</b>", reply_markup=back_menu_kb())
    set_state(c.from_user.id, "adding_sbp")
    await c.answer()


@dp.callback_query_handler(lambda c: c.data == "add_card_rf")
async def cb_add_card_rf(c: types.CallbackQuery):
    await send_photo_with_caption(c.from_user.id, "<b>💳 Добавление банковской карты (РФ)</b>\n\nПожалуйста, введите номер банковской карты в формате:\n<b>XXXX XXXX XXXX XXXX</b>", reply_markup=back_menu_kb())
    set_state(c.from_user.id, "adding_card_rf")
    await c.answer()


@dp.callback_query_handler(lambda c: c.data == "add_card_ua")
async def cb_add_card_ua(c: types.CallbackQuery):
    await send_photo_with_caption(c.from_user.id, "<b>💳 Добавление банковской карты (UA)</b>\n\nПожалуйста, введите номер банковской карты в формате:\n<b>XXXX XXXX XXXX XXXX</b>", reply_markup=back_menu_kb())
    set_state(c.from_user.id, "adding_card_ua")
    await c.answer()


@dp.callback_query_handler(lambda c: c.data == "set_stars")
async def cb_set_stars(c: types.CallbackQuery):
    user = ensure_user(c.from_user)
    user["wallets"] = {"type": "STARS"}
    save_data()
    await send_photo_with_caption(c.from_user.id, "<b>✅ Настройки обновлены: валюта сделок — STARS</b>", reply_markup=back_menu_kb())
    await c.answer()


@dp.callback_query_handler(lambda c: c.data == "create_deal")
async def cb_create_deal(c: types.CallbackQuery):
    await send_photo_with_caption(c.from_user.id, "<b>💼Создание сделки</b>\n\nВведите сумму в RUB например: 3000", reply_markup=back_menu_kb())
    set_state(c.from_user.id, "deal_amount")
    await c.answer()


@dp.callback_query_handler(lambda c: c.data == "referral")
async def cb_referral(c: types.CallbackQuery):
    user = ensure_user(c.from_user)
    uid = user['id']
    link = f"https://t.me/{(await bot.get_me()).username}?start=ref={uid}"
    caption = f"<b>🔗 Ваша реферальная ссылка:</b>\n{link}\n\n👥 Количество рефералов: {user.get('referrals',0)}\n💰 Заработано с рефералов: {user.get('balance',0.0)} RUB\nВы получаете 20% от комиссии бота с рефералов."
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🔙 Вернутся в меню", callback_data="back_menu"))
    await send_photo_with_caption(c.from_user.id, caption, reply_markup=kb)
    await c.answer()


@dp.callback_query_handler(lambda c: c.data == "lang")
async def cb_lang(c: types.CallbackQuery):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("Русский", callback_data="set_lang_ru"), InlineKeyboardButton("English", callback_data="set_lang_en"))
    await send_photo_with_caption(c.from_user.id, "Выберите язык:", reply_markup=kb)
    await c.answer()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("exitdeal_"))
async def cb_exit_deal(c: types.CallbackQuery):
    deal_id = c.data.split("_",1)[1]
    deal = DATA["deals"].get(deal_id)
    if deal:
        seller_chat = int(deal['seller_id'])
        try:
            await send_photo_with_caption(seller_chat, f"👤 Пользователь @{c.from_user.username} ({c.from_user.id}) покинул сделку #{deal_id}.\nСделка возвращена в исходное состояние и снова доступна другим покупателям.")
        except Exception:
            pass
        deal.pop('buyer_id', None)
        save_data()
    await send_photo_with_caption(c.from_user.id, "❌ Вы успешно вышли из сделки.", reply_markup=back_menu_kb())
    await c.answer()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("exitdealbtn_"))
async def cb_exit_deal_btn(c: types.CallbackQuery):
    await cb_exit_deal(c)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("confirm_payment_"))
async def cb_confirm_payment(c: types.CallbackQuery):
    deal_id = c.data[len("confirm_payment_"):]  # <-- берём только часть после префикса
    deal = DATA["deals"].get(deal_id)
    if not deal:
        await c.answer("Сделка не найдена.")
        return
    if c.from_user.id not in ADMIN_IDS:
        await c.answer("Только администратор может подтвердить оплату.")
        return
    deal['paid'] = True
    save_data()
    await send_photo_with_caption(
        int(deal['seller_id']),
        f"💰 Оплата подтверждена.\nПокупатель @{deal['buyer_username']} ({deal['buyer_id']}) оплатил ваш товар.\nПередайте подарок.",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("Я передал товар 💎", callback_data=f"delivered_{deal_id}")
        )
    )
    await c.answer("Оплата подтверждена")

@dp.callback_query_handler(lambda c: c.data and c.data.startswith("delivered_"))
async def cb_delivered(c: types.CallbackQuery):
    deal_id = c.data.split("_",1)[1]
    deal = DATA["deals"].get(deal_id)
    if not deal:
        await c.answer()
        return
    buyer_id = int(deal.get('buyer_id')) if deal.get('buyer_id') else None
    if buyer_id:
        try:
            await send_photo_with_caption(buyer_id, f"Продавец @{c.from_user.username} отправил подарок, пожалуйста подтвердите его получение", reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("Я получил подарок", callback_data=f"received_{deal_id}")))
        except Exception:
            pass
    await send_photo_with_caption(c.from_user.id, "Заказ успешно завершен!", reply_markup=back_menu_kb())
    await c.answer()

@dp.message_handler(commands=["addadmin"])
async def cmd_addadmin(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.reply("⛔ У вас нет прав для добавления админов.")
        return
    args = message.get_args().strip()
    if not args.isdigit():
        await message.reply("⚠️ Использование: /addadmin <user_id>")
        return
    new_admin = int(args)
    if new_admin in ADMIN_IDS:
        await message.reply("⚠️ Этот пользователь уже является админом.")
        return
    ADMIN_IDS.append(new_admin)
    save_admins()
    await message.reply(f"✅ Пользователь с ID {new_admin} добавлен в админы.")

@dp.message_handler(commands=["admins"])
async def cmd_admins(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.reply("⛔ У вас нет доступа к списку админов.")
        return
    admins_list = "\n".join([str(a) for a in ADMIN_IDS])
    await message.reply(f"📋 Список админов:\n{admins_list}")

@dp.callback_query_handler(lambda c: c.data and c.data.startswith("received_"))
async def cb_received(c: types.CallbackQuery):
    deal_id = c.data.split("_",1)[1]
    deal = DATA["deals"].get(deal_id)
    if not deal:
        await c.answer()
        return
    seller = int(deal['seller_id'])
    await send_photo_with_caption(c.from_user.id, "Спасибо за подтверждение!", reply_markup=back_menu_kb())
    await send_photo_with_caption(seller, "Заказ успешно завершен!", reply_markup=back_menu_kb())
    deal['completed'] = True
    deal['seller_success'] = deal.get('seller_success',0) + 1
    save_data()
    await c.answer()
@dp.message_handler()
async def handle_messages(message: types.Message):
    user = ensure_user(message.from_user)
    state = get_state(message.from_user.id)

    if state == "adding_ton":
        addr = message.text.strip()
        if not is_valid_ton(addr):
            await send_photo_with_caption(message.chat.id, "❌ Неверный формат TON-кошелька. Пример: EQCzD2l...", reply_markup=ton_back_kb())
            return
        user['wallets'] = {"type": "ton", "ton": addr}
        save_data()
        clear_state(message.from_user.id)
        await send_photo_with_caption(message.chat.id, "<b>✅ TON-кошелек успешно добавлен!</b>", reply_markup=back_menu_kb())
        return

    if state == "adding_sbp":
        phone = message.text.strip()
        if not is_valid_sbp(phone):
            await send_photo_with_caption(message.chat.id, "❌ Неверный формат СБП. Попробуйте еще раз.", reply_markup=back_menu_kb())
            return
        user['wallets'] = {"type": "sbp", "sbp": phone}
        save_data()
        clear_state(message.from_user.id)
        await send_photo_with_caption(message.chat.id, "<b>✅ СБП успешно добавлен!</b>", reply_markup=back_menu_kb())
        return

    if state in ("adding_card_rf", "adding_card_ua"):
        card = message.text.strip()
        if not is_valid_card(card):
            await send_photo_with_caption(message.chat.id, "❌ Неверный формат карты. Введите 16 цифр, пробелы допускаются.", reply_markup=back_menu_kb())
            return
        digits = re.sub(r"\D", "", card)
        if state == "adding_card_rf":
            user['wallets'] = {"type": "card", "card_number": digits, "country": "RF"}
            save_data()
            await send_photo_with_caption(message.chat.id, "🏦 Пожалуйста, уточните, какой у вас банк!", reply_markup=back_menu_kb())
            set_state(message.from_user.id, "adding_card_rf_bank")
            return
        else:
            user['wallets'] = {"type": "card", "card_number": digits, "country": "UA"}
            save_data()
            clear_state(message.from_user.id)
            await send_photo_with_caption(message.chat.id, "<b>✅ Кошелек успешно добавлен/изменен!</b>", reply_markup=back_menu_kb())
            return

    if state.startswith("adding_card_"):
        digits = re.sub(r"\D", "", message.text)
        if len(digits) != 16:
            await send_photo_with_caption(message.chat.id, "❌ Неверный формат карты. Введите 16 цифр.", reply_markup=back_menu_kb())
            return
        method = state.split("_")[-1]
        user['wallets'] = {
            "type": "card",
            "method": method,
            "card_number": digits
        }
        save_data()
        clear_state(message.from_user.id)
        await send_photo_with_caption(message.chat.id, f"✅ Кошелек {method.upper()} успешно добавлен!", reply_markup=back_menu_kb())

    if state == "adding_card_rf_bank":
        bank = message.text.strip()
        user['wallets']['bank'] = bank
        save_data()
        clear_state(message.from_user.id)
        await send_photo_with_caption(message.chat.id, "<b>✅ Кошелек успешно добавлен/изменен!</b>", reply_markup=back_menu_kb())
        return
    if state == "deal_amount":
        text = message.text.strip()
        if not text.isdigit():
            await send_photo_with_caption(message.chat.id, "Пожалуйста, введите сумму числом, например: 3000", reply_markup=back_menu_kb())
            return
        USER_STATE[f"{message.from_user.id}_deal_amount"] = text
        set_state(message.from_user.id, "deal_description")
        await send_photo_with_caption(message.chat.id, "<b>📝Укажите, что вы предлагаете в этой сделке:</b>\n\nПример: 10 Кепок и Пепе...", reply_markup=back_menu_kb())
        return

    if state == "deal_description":
        desc = message.text.strip()
        amount = USER_STATE.pop(f"{message.from_user.id}_deal_amount", "0")
        deal_id = gen_deal_id()
        DATA['deals'][deal_id] = {
               'id': deal_id,
               'seller_id': str(message.from_user.id),
               'seller_username': message.from_user.username or message.from_user.first_name,
               'amount': amount,
               'currency': 'RUB',  # вместо 'STARS'
               'description': desc,
               'pay_address': '',  # будет динамически в зависимости от выбранного способа оплаты
               'seller_success': random.randint(10, 160)
        }
        save_data()
        caption = (f"<b>✅ Сделка успешно создана!</b>\n\n"
                   f"<b>💰Сумма:</b> {amount} {DATA['deals'][deal_id]['currency']}\n"
                   f"<b>📜 Описание:</b> {desc}\n"
                   f"<b>🔗 Ссылка для покупателя:</b> https://t.me/{(await bot.get_me()).username}?start={deal_id}")
        kb = InlineKeyboardMarkup(row_width=1)
        kb.add(InlineKeyboardButton("❌ Отменить сделку", callback_data=f"cancel_{deal_id}"), InlineKeyboardButton("🔙 Вернутся в меню", callback_data="back_menu"))
        await send_photo_with_caption(message.chat.id, caption, reply_markup=kb)
        clear_state(message.from_user.id)
        return
    caption = (
        "<b>Добро пожаловать в ELF OTC – надёжный P2P-гарант</b>\n\nВыберите нужный раздел ниже:\n"
    )
    kb = main_menu_kb(message.from_user.id)
    await send_photo_with_caption(message.chat.id, caption, reply_markup=kb)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("cancel_"))
async def cb_cancel(c: types.CallbackQuery):
    deal_id = c.data.split("_",1)[1]
    if deal_id in DATA['deals']:
        DATA['deals'].pop(deal_id)
        save_data()
    await send_photo_with_caption(c.from_user.id, "Сделка отменена.", reply_markup=back_menu_kb())
    await c.answer()
if __name__ == '__main__':
    print("Bot starting...")
    if not PHOTO_PATH:
        print("Warning: no photo found in 'lil/' folder. All messages will fall back to text.")
    executor.start_polling(dp, skip_updates=True)
