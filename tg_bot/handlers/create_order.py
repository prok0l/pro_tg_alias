from aiogram import types, Dispatcher
from aiogram.types import PreCheckoutQuery

from tg_bot.services.db_api import DBApi
from tg_bot.services.data.items import One_limit
from tg_bot.services.consts import Order

db_obj: DBApi


async def show_invoices(message: types.Message):
    await message.bot.send_invoice(message.from_user.id,
                                   **One_limit.generate_invoice(),
                                   payload="+1")


async def successful_payment(message: types.Message):
    await message.answer(Order.SUCCESSFUL.value)
    db_obj.plus_one_limit(tg_id=message.from_user.id)


def registrer_invoice(dp: Dispatcher, db: DBApi):
    global db_obj
    db_obj = db
    dp.register_message_handler(callback=show_invoices, commands=['pay'])

    @dp.pre_checkout_query_handler(lambda query: True)
    async def pre_checkout_query(pre_check_query: PreCheckoutQuery):
        await dp.bot.answer_pre_checkout_query(pre_check_query.id, ok=True)

    dp.register_message_handler(callback=successful_payment,
                                content_types=types.ContentType.
                                SUCCESSFUL_PAYMENT)
