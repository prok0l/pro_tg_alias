from aiogram import types, Dispatcher


from tg_bot.services.consts import Help, AdminHelp

ADMINS: list


async def bot_help(message: types.Message):
    if message.from_user.id not in ADMINS:
        await message.answer("".join([*Help]))
    else:
        await message.answer("".join([*Help]+[*AdminHelp]))


def register_help(dp: Dispatcher, admins: list):
    global ADMINS
    ADMINS = admins
    dp.register_message_handler(callback=bot_help, commands=['help'],
                                content_types="text", state=None)
