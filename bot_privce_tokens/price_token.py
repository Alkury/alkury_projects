import requests
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Replace these values with your own
TOKEN = 'TOKEN'  # токен бота из @botfather
CHANNEL_ID = '@sdfsdfsdfawde'  # канал куда будет бот постить курс. Вроде как работает как и id, но лучше указывать @
bot = Bot(token=TOKEN)
dp = Dispatcher()
stop_event = asyncio.Event()


async def send_message(message):
    last_price = 1
    text_after_start = message.text.split(" ")
    if len(text_after_start) >= 5:
        await message.answer("Бот запущен.")
        print(text_after_start, text_after_start[2])
        network = "ton"  # сеть в которой токен наш находится пример: ton, eth, sol
        network_ton = "eth"  # не трогать это для курса тона в баксах
        adress_token = text_after_start[1]  # c сайта https://www.geckoterminal.com/ru
        adres_ton = "0x582d872a1b094fc48f5de31d3b73f2d9be47def1"  # этот адрес с того же сайта, но тут чисто как прайс в другой сети
        url_token = f"https://api.geckoterminal.com/api/v2/networks/{network}/tokens/multi/{adress_token}"
        url_ton = f"https://api.geckoterminal.com/api/v2/networks/{network_ton}/tokens/multi/{adres_ton}"
        url_swap = text_after_start[3]  # ссылка под сообщением
        nuls_after_point = int(text_after_start[2])  # тут колво знаком после точки для m5 это 4, типа: 1.0303
        #                                                                                                |    | <--- 4 знака
        text_in_button = " ".join(text_after_start[4:])
        while not stop_event.is_set():
            button = InlineKeyboardButton(
                text=text_in_button,
                url=url_swap
            )
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]])

            response_m5 = requests.get(url_token)
            price_token = round(float(response_m5.json()["data"][0]['attributes']['price_usd']), nuls_after_point)
            await asyncio.sleep(15)
            response_ton = requests.get(url_ton)
            price_ton = round(float(response_ton.json()["data"][0]['attributes']['price_usd']), nuls_after_point)

            if price_token / last_price - 1 > 0:
                emoji = "🟢"
            elif price_token / last_price - 1 == 0:  # это чисто от меня, а то глупо выглядит
                emoji = "⚪️"
            else:
                emoji = "🔴"

            text_in_post = f"${price_token} ({round(price_token / price_ton, 6)}💎) {emoji} {round((price_token / last_price - 1) * 100, 2)}%"  # тут сделал фикс колво курса в тоне до 6 знаков после запятой, но омжно и самому выставить нужное
            await bot.send_message(chat_id=CHANNEL_ID, text=text_in_post, reply_markup=keyboard)
            last_price = price_token
            await asyncio.sleep(20)
    else:
        await message.answer(
            "Неверный формат ввода, посмотрите на формулу:\n\n <code>/start adress_token nuls_after_point link_in_button text_in_button</code>",
            parse_mode="HTML")


# Пример :)
# /start adress_token nuls_after_point link_in_button text_in_button
# /start EQBa6Oofc4vQZ1XZLTYRkbX4qWUWBCf0sFBgo0kdxdlw6rqN 4 https://swap.coffee/dex?ft=TON&st=M5 Buy M5
@dp.message(Command('start'))
async def start_handler(message: types.Message):
    await send_message(message)


@dp.message(Command('stop'))
async def stop_handler(message: types.Message):
    stop_event.set()
    await message.answer("Бот остановлен.")


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
