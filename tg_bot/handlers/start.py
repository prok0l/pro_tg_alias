import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Command


async def bot_start(message: types.Message):
    await message.answer("Привет, я telegram bot для игры в <b>Alias</b>, "
                        "с возможностью создания собственной колоды")
    id_user = message.from_user.id
    # TODO добавить добавление или поиск в бд


def register_start(dp: Dispatcher):
    dp.register_message_handler(callback=bot_start, commands=['start'],
                                content_types="text", state=None)