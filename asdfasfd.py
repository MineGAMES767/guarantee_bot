import asyncio
import random
import time

import aiohttp
from typing import List
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery
from aiogram import Router, F

# Конфигурация
API_TOKEN = '8410269448:AAH6_4Qm_LPEVd5AyPEQSKb2Of7AS61FVfE'

router = Router()

# Более актуальный список подарков (некоторые из старых могут не работать)
ALL_GIFT = [
    "LunarSnake", "SnakeBox", "XmasStocking", "BDayCandle", "LolPop", "StarNotepad", "InstantRamen", "SpringBasket", "StellarRocket" , "BerryBox",
    "SleighBell", "MousseCake", "EasterEgg", "SantaHat", "DeskCalendar", "NekoHelmet", "EternalRose", "JingleBells", "JesterHat", "WinterWreath",
    "WhipCupcake", "EternalCandle", "LoveCandle", "BunnyMuffin", "GingerCookie", "HomemadeCake", "EvilEye", "SpicedWine", "SnowGlobe"
]

# Кэш рабочих ссылок (чтобы не проверять одни и те же повторно)
link_cache = set()

strtkb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Поиск 🚀", callback_data="get_gift")]
])


@router.callback_query(F.data == "get_gift")
async def get_gift_handler(callback: CallbackQuery):
    await callback.answer("Генерирую ссылки...")

    # Используем asyncio.sleep вместо time.sleep для асинхронной работы
    await asyncio.sleep(0.5)

    links = []
    for _ in range(100):
        rand = random.randint(1000, 99999)
        random_gift = random.choice(ALL_GIFT)
        link = f"https://t.me/nft/{random_gift}-{rand}"
        links.append(f"{_+1}. {link}")

    # Объединяем все ссылки в одно сообщение
    links_text = "\n\n".join(links)

    await callback.message.answer(links_text, reply_markup=strtkb)



@router.message(Command("start"))
async def start(message: Message):
    welcome_text = """🎁 *Бот для поиска подарков в Telegram*

Как это работает:
1. Нажимайте кнопку "Получить подарок"
2. Проверяйте ссылку
3. Отмечайте, работает она или нет
4. Бот учится и предлагает более точные ссылки

*Важно:* Некоторые ссылки могут не работать, это нормально."""

    await message.answer(
        text=welcome_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=strtkb
    )


async def main():
    print("Бот запущен!")

    bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)

    await bot.set_my_commands([
        types.BotCommand(command="start", description="Запустить бота")
    ])

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())