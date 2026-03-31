import asyncio
import html
import logging
import os

from aiogram import Bot, Dispatcher, Router
from aiogram.enums import MessageEntityType
from aiogram.filters import Command
from aiogram.types import Message

import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = Router()


def utf16_entity_slice(text: str, offset: int, length: int) -> str:
    """Срез текста по offset/length в UTF-16 code units (как в Telegram API)."""
    units = 0
    start_idx = None
    for i, ch in enumerate(text):
        if units == offset:
            start_idx = i
            break
        units += 2 if ord(ch) > 0xFFFF else 1
    if start_idx is None:
        return ""

    units = 0
    out: list[str] = []
    for i in range(start_idx, len(text)):
        ch = text[i]
        ch_units = 2 if ord(ch) > 0xFFFF else 1
        if units + ch_units > length:
            break
        out.append(ch)
        units += ch_units
        if units == length:
            break
    return "".join(out)


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Пришлите сообщение с кастомными эмоджи (Telegram Premium / наборы эмоджи). "
        "Бот ответит списком custom_emoji_id для каждого такого эмоджи.\n\nDev: @alkury"
    )


@router.message(Command("ex"))
async def cmd_start(message: Message) -> None:
    t = """text_menu = (f"<tg-emoji emoji-id='5373144051690258848'>📱</tg-emoji> <b>Меню Steam</b>")\n"""
    t += "await msg.answer(text=t, parse_mode='html')"
    await message.answer(
        f"Ниже приведены примеры использование кастомных эмоджи:\n\n- для текста:\n{t}"
    )


@router.message()
async def show_custom_emoji_codes(message: Message) -> None:
    text = message.text or message.caption
    if not text:
        await message.answer("Нужен текст (или подпись к медиа) с кастомными эмоджи.")
        return

    entities = message.entities or message.caption_entities
    if not entities:
        await message.answer(
            "В сообщении нет кастомных эмоджи. "
            "Отправьте именно кастомные эмоджи из Telegram."
        )
        return

    lines: list[str] = []
    for entity in entities:
        if entity.type != MessageEntityType.CUSTOM_EMOJI:
            continue
        eid = entity.custom_emoji_id
        if not eid:
            continue
        fragment = utf16_entity_slice(text, entity.offset, entity.length)
        preview = fragment or "—"
        lines.append(
            f"• <tg-emoji emoji-id='{html.escape(eid)}'>{html.escape(preview)}</tg-emoji> → <code>{html.escape(eid)}</code>"
        )

    if not lines:
        await message.answer(
            "Кастомных эмоджи не найдено. Убедитесь, что в тексте есть эмоджи из набора Telegram "
        )
        return

    await message.answer(
        "Найденные кастомные эмоджи:\n\n" + "\n".join(lines),
        parse_mode="HTML",
    )


def _token() -> str:
    return (os.environ.get("BOT_TOKEN") or config.BOT_TOKEN or "").strip()


async def main() -> None:
    token = _token()
    if not token:
        raise SystemExit("Укажите BOT_TOKEN в config.py или переменную окружения BOT_TOKEN.")

    bot = Bot(token=token)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
