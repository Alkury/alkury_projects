import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from aiogram import F

bot = Bot(token="TOKEN")
dp = Dispatcher()
id_admin = "ваш id"  # 979360464


@dp.message(Command('start'))
async def start(message: Message):
    await bot.send_message(chat_id=message.chat.id,
                           text="Привет! Это бот обратной связи с @alkury. Напиши любое сообщение и я доставлю его @alkury")


@dp.message(Command('ans'))
async def answer(message: Message):
    if message.chat.id == id_admin:
        text = message.text.split(" ")
        print(text)
        if len(text) >= 3:
            id_user = text[1]
            await bot.send_message(chat_id=id_user,
                                   text=" ".join(text[2:]))
        else:
            await bot.send_message(chat_id=id_admin,
                                   text=f"Неверный формат ответа, введите: \n<code>/ans ~id_user~ ~text~ </code>",
                                   parse_mode="HTML")


@dp.message(Command('ban'))
async def answer(message: Message):
    if message.chat.id == id_admin:
        text = message.text.split(" ")
        print(text)
        if len(text) == 2:
            with open("blacklist.txt", "r+") as blacklist:
                blacklist.readlines()
                if text[1] not in blacklist:
                    blacklist.write(text[1] + "\n")
                    print(text[1])
                    await message.reply(f"Пользователь с id <code>{text[1]}</code> добавлен в чс",
                                        parse_mode="HTML")
        else:
            await bot.send_message(chat_id=id_admin,
                                   text=f"Неверный формат ответа, введите: \n<code>/ban ~id_user~</code>",
                                   parse_mode="HTML")


# тг @alkury
@dp.message(F.text)
async def send_message(message: Message):
    blacklist = open("blacklist.txt", "r").readlines()
    print(blacklist)
    if str(message.chat.id) + '\n' not in blacklist:
        if message.from_user.username:
            await bot.send_message(chat_id=id_admin,
                                   text=f"Cообщение от {message.from_user.first_name} (@{message.from_user.username}, <code>{message.chat.id}</code>): \n\n{message.text}",
                                   parse_mode="HTML")
        else:
            await bot.send_message(chat_id=id_admin,
                                   text=f"Cообщение от {message.from_user.first_name} (<code>{message.chat.id}</code>): \n\n{message.text}",
                                   parse_mode="HTML")
    else:
        await bot.send_message(chat_id=message.chat.id, text=f"Вы находитесь в чс у админа")


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
