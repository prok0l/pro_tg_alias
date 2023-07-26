import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import StatesGroup, State

from tg_bot.services.db_api import DBApi
from tg_bot.services.consts import AddDeckButtons, AddDeckText, CancelText

db_obj: DBApi


class AddDeckSM(StatesGroup):
    waiting_for_button = State()


async def add_deck_start(message: types.Message, state: FSMContext):
    deck_id = message.get_args()

    # проверка на id
    if not deck_id or not deck_id.isdigit():
        await message.answer(AddDeckText.INVALID_ID.value)
        return None

    # проверка на существование колоды
    if not db_obj.check_deck_id(deck_id=deck_id):
        await message.answer(AddDeckText.NO_ID.value)
        return None

    name = db_obj.deck_info(tg_id=message.from_user.id, deck_id=deck_id)
    # проверка на добавление раньше
    if not name:
        await message.answer(AddDeckText.ADDED_EARLIER.value)
        return None

    kbd = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kbd.add(*AddDeckButtons)
    # ожидание выбора пользователем Да/Нет
    await message.answer(AddDeckText.CHECKING_QUESTION.value.format(name=name),
                         reply_markup=kbd)
    await state.set_state(AddDeckSM.waiting_for_button.state)
    await state.update_data(deck_id=deck_id)


async def btn(message: types.Message, state: FSMContext):
    # проверка, что это нажатие кнопки, а не случайный текст
    if message.text not in [*AddDeckButtons]:
        await message.answer(AddDeckText.INVALID_BTN.value)
        return None

    data = await state.get_data()
    kbd = types.ReplyKeyboardRemove()
    # обработка нажатия кнопки Да (добавление колоды)
    if message.text == AddDeckButtons.YES.value:
        db_obj.add_deck(tg_id=message.from_user.id,
                        deck_id=data["deck_id"])
        await message.answer(AddDeckText.ADDED.value, reply_markup=kbd)
    # обработка нажатия кнопки Нет (Отмена)
    else:
        await message.answer(CancelText.CANCEL.value, reply_markup=kbd)
    await state.finish()


def register_add_deck(dp: Dispatcher, db: DBApi):
    global db_obj
    db_obj = db
    dp.register_message_handler(callback=add_deck_start, commands=['add_deck'],
                                content_types="text", state="*")
    dp.register_message_handler(callback=btn,
                                state=AddDeckSM.waiting_for_button)
