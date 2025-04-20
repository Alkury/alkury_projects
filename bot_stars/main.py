import asyncio
import logging
from typing import Optional

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, PreCheckoutQuery, LabeledPrice, InlineKeyboardButton, InlineKeyboardMarkup
from pydantic_settings import BaseSettings
from bot_stars import config


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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


class GiftStates(StatesGroup):
    waiting_for_gift_id = State()
    waiting_for_amount = State()


class GiftPremiumStates(StatesGroup):
    waiting_for_input = State()


def create_payment_keyboard(amount: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardMarkup(inline_keyboard=[])
    builder.inline_keyboard.append([InlineKeyboardButton(text=f"Оплатить {amount} ⭐️", pay=True)])
    return builder


@router.message(Command("start"))
async def start_handler(message: Message, state: FSMContext) -> None:
    await message.answer("Привет! Введите количество звёзд для пожертвования:")
    await state.set_state(GiftStates.waiting_for_amount)


@router.message(Command("paysupport"))
async def paysupport_handler(message: Message) -> None:
    last_message: Optional[Message] = message.reply_to_message
    if last_message:
        logger.info(f"Reply message: {last_message.text}")
    await message.answer("Добровольные пожертвования не подразумевают возврат средств, "
                         "однако, если вы очень хотите вернуть средства - свяжитесь с нами.")


@router.message(Command("gift"))
async def gift_handler(message: Message, state: FSMContext) -> None:
    if message.chat.id != settings.ADMIN_CHAT_ID:
        await message.answer("вы не админ), пишите @alkury для покупки подарков через бота")
        return
    await message.answer("Введите идентификатор подарка, ID пользователя и количество, разделенные пробелом:")
    await state.set_state(GiftStates.waiting_for_gift_id)


@router.message(Command("gift_premium"))
async def gift_premium_handler(message: Message, state: FSMContext) -> None:
    if message.chat.id != settings.ADMIN_CHAT_ID:
        await message.answer("вы не админ), пишите @alkury для покупки подарков через бота")
        return
    await message.answer("Введите ID пользователя и количество месяцев (3, 6 или 12), разделенные пробелом:")
    await state.set_state(GiftPremiumStates.waiting_for_input)


@router.message(GiftStates.waiting_for_amount)
async def process_amount(message: Message, state: FSMContext) -> None:
    try:
        amount = int(message.text)
        prices = [LabeledPrice(label="XTR", amount=amount)]
        keyboard = create_payment_keyboard(amount)

        await message.answer_invoice(title="Поддержка канала", description=f"Поддержать канал на {amount} звёзд!",
            prices=prices, provider_token="", payload="channel_support", currency="XTR", reply_markup=keyboard, )
        await state.clear()
    except ValueError:
        await message.answer("Некорректный ввод. Пожалуйста, введите целое число.")


@router.message(GiftStates.waiting_for_gift_id)
async def process_gift_id(message: Message, state: FSMContext) -> None:
    if message.chat.id != settings.ADMIN_CHAT_ID:
        await message.answer("вы не админ), пишите @alkury для покупки подарков через бота")
        await state.clear()
        return
    try:
        text = message.text.split()
        if len(text) != 3:
            raise ValueError
        gift_id, user_id, almost = text[0], int(text[1]), int(text[2])
        for _ in range(almost):
            await bot.send_gift(user_id=user_id, gift_id=gift_id)
        await message.answer("Подарки отправлены успешно!")
    except (ValueError, Exception) as e:
        await message.answer("Некорректный ввод. Формат: <gift_id> <user_id> <количество>")
    finally:
        await state.clear()


@router.message(GiftPremiumStates.waiting_for_input)
async def process_gift_premium_input(message: Message, state: FSMContext) -> None:
    if message.chat.id != settings.ADMIN_CHAT_ID:
        await message.answer("вы не админ), пишите @alkury для покупки подарков через бота")
        await state.clear()
        return
    try:
        text = message.text.split()
        if len(text) != 2:
            raise ValueError
        user_id = int(text[0])
        month_count = int(text[1])
        if month_count not in [3, 6, 12]:
            raise ValueError
        star_count_map = {3: 1000, 6: 1500, 12: 2500}
        star_count = star_count_map[month_count]
        result = await bot.gift_premium_subscription(user_id=user_id, month_count=month_count, star_count=star_count,
            text="Premium subscription gifted by admin!")
        await message.answer(
            "Premium subscription gifted successfully!" if result else "Failed to gift premium subscription.")
    except (ValueError, Exception) as e:
        await message.answer("Invalid input. Please provide user ID and month count (3, 6, or 12) separated by space.")
    finally:
        await state.clear()


@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery) -> None:
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def success_payment_handler(message: Message) -> None:
    total_amount = message.successful_payment.total_amount
    logger.info(f"Successful payment: {total_amount} XTR")
    await bot.send_message(settings.ADMIN_CHAT_ID,
        f"Обманули гоя на: {total_amount}⭐({round(total_amount * 0.013, 3)}$) @{message.chat.username}")


# Основная функция
async def main() -> None:
    dp.include_router(router)
    try:
        logger.info("Bot started")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")


if __name__ == "__main__":
    asyncio.run(main())
