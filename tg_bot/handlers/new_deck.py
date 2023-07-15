import os

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from tg_bot.services.db_api import DBApi
from tg_bot.services.consts import Path, DeckTypes
from tg_bot.services.file_filter import file_filter

db_obj: DBApi = None


class OrderDeck(StatesGroup):
    waiting_for_name = State()
    waiting_for_file = State()


async def duration_start(message: types.Message, state: FSMContext):
    if db_obj.is_max_decks(tg_id=message.from_user.id):
        await message.answer("У вас максимальное количество колод")
        return
    await message.answer("Напишите название новой колоды:  ")
    await state.set_state(OrderDeck.waiting_for_name.state)


async def name_chosen(message: types.Message, state: FSMContext):
    if not db_obj.check_deck_name(deck_name=message.text):
        await message.answer("Извините, это название уже занято")
        return None
    await state.update_data(name=message.text)
    await state.set_state(OrderDeck.waiting_for_file.state)
    await message.answer("Теперь пришлите файл с расширением txt")


async def file_chosen(message: types.Message, state: FSMContext):
    file_id = message.document.file_id
    file = await message.bot.get_file(file_id)
    path = str(max(int(x.split(".")[0]) for x in os.listdir(Path.decks.value +
                                                            '.')) + 1) + ".txt"
    await message.bot.download_file(file_path=file.file_path,
                                    destination=Path.decks.value + path)
    file_filter(Path.decks.value + path)
    data = await state.get_data()
    deck_id = db_obj.new_deck(tg_id=message.from_user.id,
                              name=data["name"], path=path)
    await message.answer(f"Добавлена колода - {data['name']}\n"
                         f"Статус {DeckTypes.Private.value} "
                         f"можно изменить в меню колод.\n"
                         f"id колоды - <code>{deck_id}</code>")


async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Действие отменено")


def register_new_deck(dp: Dispatcher, db: DBApi):
    global db_obj
    db_obj = db
    dp.register_message_handler(callback=duration_start, commands=["new_deck"],
                                state="*")
    dp.register_message_handler(callback=cmd_cancel, commands=["cancel"],
                                state=[OrderDeck.waiting_for_file,
                                       OrderDeck.waiting_for_name])
    dp.register_message_handler(callback=name_chosen,
                                state=OrderDeck.waiting_for_name)
    dp.register_message_handler(callback=file_chosen,
                                state=OrderDeck.waiting_for_file,
                                content_types=types.ContentType.DOCUMENT)
