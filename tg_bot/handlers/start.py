import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Command

from tg_bot.services.db_api import DBApi
from tg_bot.services.consts import Start

db_obj: DBApi


async def bot_start(message: types.Message):
    await message.answer(Start.START.value)
    id_user = message.from_user.id
    if message.from_user.username:
        username = message.from_user.username
    else:
        username = message.from_user.first_name
        if message.from_user.last_name:
            username += " " + message.from_user.last_name
    db_obj.create_user(tg_id=id_user, username=username)


def register_start(dp: Dispatcher, db: DBApi):
    global db_obj
    db_obj = db
    dp.register_message_handler(callback=bot_start, commands=['start'],
                                content_types="text", state=None)
