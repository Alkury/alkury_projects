import json
import logging
import asyncio
import aiofiles

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.types import Message
from pydantic_settings import BaseSettings

import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def read_json(path: str):
    async with aiofiles.open(path, mode='r', encoding='utf-8') as f:
        return json.loads(await f.read())

async def edit_json(path: str, id_gift: str, name_gift: str):
    async with aiofiles.open(path, "r", encoding="utf-8") as f:
        content = await f.read()
        data = json.loads(content)

    data["gifts"][name_gift] = id_gift

    async with aiofiles.open(path, "w", encoding="utf-8") as f:
        await f.write(json.dumps(data, indent=4, ensure_ascii=False))


class Settings(BaseSettings):
    BOT_TOKEN: str = config.API_KEY
    ADMIN_CHAT_ID: int = config.admin_id

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

BOT_TOKEN = settings.BOT_TOKEN
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()


@dp.message(Command("start"))
async def start(message: Message):
    if message.from_user.id == settings.ADMIN_CHAT_ID:
        await bot.send_message(message.chat.id,
                               f"Привет, отправь мне id подарка и его название в одну строку через пробел!\nПример:\n<code>5800655655995968830 мишка14ф</code>",
                               parse_mode="html")

@dp.message()
async def add_ids(message: Message):
    if message.from_user.id == settings.ADMIN_CHAT_ID:
        text = message.text.split(" ")
        if len(text) != 2:
            await bot.send_message(message.chat.id, "Слов должно быть 2\nПример:\n<code>5800655655995968830 мишка14ф</code>",
                               parse_mode="html")
        else:
            id_gift, name = text
            try:
                await edit_json("ids.json", id_gift, name)
                await bot.send_message(message.chat.id,
                                       f"Бот успешно добавил подарок\nОтправьте <code>.{name} текст</code> в чат с собеседником! Писать текст не обязательное поле!",
                                       parse_mode="html")
            except Exception as e:
                await bot.send_message(message.chat.id,
                                       f"Ой... какая-то ошибка",
                                       parse_mode="html")



# Основная функция
async def main() -> None:
    try:
        logger.info("Bot started")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")


if __name__ == "__main__":
    asyncio.run(main())