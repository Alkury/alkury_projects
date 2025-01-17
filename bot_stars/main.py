from aiogram import Bot, Dispatcher, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import LabeledPrice, Message, PreCheckoutQuery
from aiogram.filters import Command
from aiogram import F
from config import *

bot = Bot(token=API_KEY)
dp = Dispatcher()

# alkury
async def payment_keyboard(amount: int):
    builder = InlineKeyboardBuilder()
    builder.button(text=f"Оплатить {amount} ⭐️", pay=True)
    return builder.as_markup()


@dp.message(Command("start"))
async def send_invoice_handler(message: Message):
    await message.answer("Введите количество звёзд для пожертвования:")


@dp.message(F.text)
async def get_amount_handler(message: Message):
    try:
        amount = int(message.text)
        prices = [LabeledPrice(label="XTR", amount=amount)]
        await message.answer_invoice(
            title="Поддержка канала",
            description=f"Поддержать канал на {amount} звёзд!",
            prices=prices,
            provider_token="",
            payload="channel_support",
            currency="XTR",
            reply_markup=await payment_keyboard(amount),
        )
    except ValueError:
        await message.answer("Некорректный ввод. Пожалуйста, введите целое число.")


@dp.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)


@dp.message(F.successful_payment)
async def success_payment_handler(message: Message):
    total_amount = message.successful_payment.total_amount
    print(total_amount)
    await message.answer(text="🥳Спасибо за вашу поддержку!🤗")


@dp.message(Command("paysupport"))
async def pay_support_handler(message: Message):
    last_message = message.reply_to_message
    if last_message:
        print(last_message.text)
    await message.answer(
        text="Добровольные пожертвования не подразумевают возврат средств, "
             "однако, если вы очень хотите вернуть средства - свяжитесь с нами."
    )


if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
