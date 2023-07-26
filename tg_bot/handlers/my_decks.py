from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from tg_bot.services.db_api import DBApi
from tg_bot.services.consts import MyDecksButtons, CancelText, MyDecksText

db_obj: DBApi


class OrderDeck(StatesGroup):
    waiting_for_deck = State()
    waiting_for_btn = State()


async def my_decks_start(message: types.Message, state: FSMContext):
    decks, now_deck = db_obj.decks_by_tg_id(tg_id=message.from_user.id)
    # проверка на наличие колод
    if not decks:
        await message.answer(MyDecksText.NO_DECKS.value)
        return None
    # формирование строки с перечнем колод и нумерацией
    decks_str_lst = []
    for ind in range(len(decks)):
        if decks[ind][0] != now_deck:
            decks_str_lst.append(MyDecksText.DECK_NAME.value.format(
                ind=ind+1, name=decks[ind][1]
            ))
        else:
            decks_str_lst.append(MyDecksText.DECK_NAME_USED.value.format(
                ind=ind + 1, name=decks[ind][1]
            ))
    decks_str = "\n".join(decks_str_lst)
    await message.answer(
        decks_str + "\n" + MyDecksText.START.value
        )
    await state.update_data(decks_ids=[x[0] for x in decks])  # links
    await state.update_data(decks_str=[x[1] for x in decks])  # названия
    await state.set_state(OrderDeck.waiting_for_deck.state)


async def deck_chosen(message: types.Message, state: FSMContext):
    data = await state.get_data()
    # проверка на корректность ind
    if message.text.isdigit() and 0 < (ind := int(message.text)) <= \
            len(data["decks_ids"]):
        # запись выбранной колоды
        await state.update_data(deck_ind=ind - 1)
        kbd = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kbd.add(*MyDecksButtons)
        await message.answer(text=MyDecksText.CHOOSE_BTN.value,
                             reply_markup=kbd)
        await state.set_state(OrderDeck.waiting_for_btn.state)

    # обработка некоректного ind
    else:
        await message.answer(MyDecksText.INVALID_NUM.value)


async def btn(message: types.Message, state: FSMContext):
    data = await state.get_data()
    # проверка, что это нажатие кнопки, а не случайный текст
    if message.text not in [*MyDecksButtons]:
        await message.answer(MyDecksText.INVALID_BTN.value)
        return None

    ind = data["deck_ind"]
    # обработка смены колоды
    if message.text == MyDecksButtons.CHOOSE.value:
        db_obj.change_deck(tg_id=message.from_user.id,
                           deck_link=data["decks_ids"][ind])
        await message.answer(MyDecksText.CHOOSE_DECK.value
                             .format(name=data['decks_str'][ind]),
                             reply_markup=types.ReplyKeyboardRemove())
        await state.finish()
    # обработка удаления колоды
    else:
        db_obj.del_deck_link(tg_id=message.from_user.id,
                             deck_link=data["decks_ids"][ind])
        await message.answer(MyDecksText.DEL_DECK.value,
                             reply_markup=types.ReplyKeyboardRemove())
        await state.finish()


async def cmd_cancel(message: types.Message, state: FSMContext):
    kbd = types.ReplyKeyboardRemove()
    await state.finish()
    await message.answer(CancelText.CANCEL.value,
                         reply_markup=kbd)


def register_my_decks(dp: Dispatcher, db: DBApi):
    global db_obj
    db_obj = db
    dp.register_message_handler(callback=my_decks_start, commands=["my_decks"],
                                state="*")
    dp.register_message_handler(callback=cmd_cancel, commands=["cancel"],
                                state=[OrderDeck.waiting_for_deck,
                                       OrderDeck.waiting_for_btn])
    dp.register_message_handler(callback=deck_chosen,
                                state=OrderDeck.waiting_for_deck)
    dp.register_message_handler(callback=btn,
                                state=OrderDeck.waiting_for_btn)
