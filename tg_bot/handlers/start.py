import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Command

from tg_bot.services.db_api import DBApi


async def bot_start(message: types.Message):
    await message.answer("Привет, я telegram bot для игры в <b>Alias</b>, "
                        "с возможностью создания собственной колоды")
    id_user, username = message.from_user.id, message.from_user.username
    db_obj.create_user(tg_id=id_user, username=username)



def register_start(dp: Dispatcher, db: DBApi):
    global db_obj
    db_obj = db
    dp.register_message_handler(callback=bot_start, commands=['start'],
                                content_types="text", state=None)