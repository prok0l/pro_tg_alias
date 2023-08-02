from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from tg_bot.services.db_api import DBApi
from tg_bot.services.consts import CancelText, DecksShopText
from tg_bot.services.word import word_func

db_obj: DBApi


class DecksShopSM(StatesGroup):
    waiting_for_deck = State()


async def decks_shop_start(message: types.Message, state: FSMContext):
    decks = db_obj.decks_shop(tg_id=message.from_user.id)
    # формирование строки с перечнем колод и нумерацией
    decks_str_lst = []
    for ind in range(len(decks)):
        num_words = decks[ind][2]
        word = word_func(num_words)
        if not decks[ind][-1]:
            decks_str_lst.append(DecksShopText.DECK_NAME.value.format(
                ind=ind+1, name=decks[ind][1],
                num_words=decks[ind][2], word=word))
        else:
            decks_str_lst.append(DecksShopText.DECK_NAME_AVAILABLE.value.
                                 format(ind=ind+1, name=decks[ind][1],
                                        num_words=num_words, word=word))

    await message.answer(
        "\n".join(decks_str_lst) + "\n" + DecksShopText.START.value
        )

    await state.update_data(decks_ids=[x[0] for x in decks])  # ids
    await state.set_state(DecksShopSM.waiting_for_deck.state)


async def deck_chosen(message: types.Message, state: FSMContext):
    data = await state.get_data()
    # проверка на корректность ind
    if message.text.isdigit() and 0 < (ind := int(message.text)) <= \
            len(data["decks_ids"]):
        # запись выбранной колоды
        link = db_obj.add_deck(tg_id=message.from_user.id,
                               deck_id=data["decks_ids"][ind - 1])
        if not link:
            await message.answer(DecksShopText.ADDED_EARLIER.value)
        else:
            await message.answer(DecksShopText.ADD_DECK.value)
        await state.finish()

    # обработка некоректного ind
    else:
        await message.answer(DecksShopText.INVALID_NUM.value)


async def cmd_cancel(message: types.Message, state: FSMContext):
    kbd = types.ReplyKeyboardRemove()
    await state.finish()
    await message.answer(CancelText.CANCEL.value,
                         reply_markup=kbd)


def register_decks_shop(dp: Dispatcher, db: DBApi):
    global db_obj
    db_obj = db
    dp.register_message_handler(callback=decks_shop_start,
                                commands=["decks_shop"],
                                state="*")
    dp.register_message_handler(callback=cmd_cancel, commands=["cancel"],
                                state=DecksShopSM.waiting_for_deck)
    dp.register_message_handler(callback=deck_chosen,
                                state=DecksShopSM.waiting_for_deck)
