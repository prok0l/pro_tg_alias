import logging
from asyncio import sleep

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Command


async def bot_help(message: types.Message):
    await message.answer("Список команд:\n"
                         "/start\n"
                         "/help\n")


def register_help(dp: Dispatcher):
    dp.register_message_handler(callback=bot_help, commands=['help'],
                                content_types="text", state=None)