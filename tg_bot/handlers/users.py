from aiogram import types, Dispatcher
from tg_bot.services.db_api import DBApi

db_obj: DBApi
ADMINS: list


async def users(message: types.Message):
    if message.from_user.id not in ADMINS:
        return None
    await message.answer("\n".join(["\t".join([str(y) for y in x])
                                    for x in db_obj.users()]))


def register_users(dp: Dispatcher, db: DBApi, admins: list):
    global db_obj, ADMINS
    db_obj = db
    ADMINS = admins
    dp.register_message_handler(callback=users, commands=["users"],
                                content_types="text", state=None)
