import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Command

from tg_bot.services.db_api import DBApi

db_obj: DBApi = None


async def add_deck_start(message: types.Message):
    deck_id = message.get_args()
    if not deck_id or not deck_id.isdigit():
        await message.answer("Пожалуйста, после команды укажите id колоды, "
                             "которую вы хотите добавить")
        return None
    if not db_obj.check_deck_id(deck_id=deck_id):
        await message.answer("Простите, но колоды с таким id не существует")
        return None
    if not db_obj.add_deck(tg_id=message.from_user.id, deck_id=deck_id):
        await message.answer("Эта колода уже была добавлена ранее")
        return None
    await message.answer("Колода успешно добавлена")


def register_add_deck(dp: Dispatcher, db: DBApi):
    global db_obj
    db_obj = db
    dp.register_message_handler(callback=add_deck_start, commands=['add_deck'],
                                content_types="text", state=None)
