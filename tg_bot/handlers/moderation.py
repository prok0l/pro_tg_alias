from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from tg_bot.services.db_api import DBApi
from tg_bot.services.consts import ModerationText, Path, ModerationButtons, \
    DeckTypes, CancelText

db_obj: DBApi
ADMINS: list


class ModerationSM(StatesGroup):
    waiting_for_ind = State()
    waiting_for_type = State()


async def moderation(message: types.Message, state: FSMContext):
    # проверка что сообщение от админа
    if message.from_user.id not in ADMINS:
        return None

    # получение колод на модерации
    decks = db_obj.moderation()

    # обработка отсутствия колод
    if not decks:
        await message.answer(ModerationText.NO_DECKS.value)
        return None

    decks_str = ModerationText.START_FULL.value.format(str="\n".join(
        ModerationText.START.value.format(x=decks[i], ind=i + 1)
        for i in range(len(decks))))
    await message.answer(decks_str)
    await state.set_state(ModerationSM.waiting_for_ind.state)
    await state.update_data(decks=decks)


async def wait_for_ind(message: types.Message, state: FSMContext):
    data = await state.get_data()
    # проверка ind
    if message.text.isdigit() and\
            (ind := int(message.text)) <= len(data["decks"]):
        await state.update_data(ind=ind - 1)
        now_deck = data["decks"][ind - 1]

        kbd = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kbd.add(*ModerationButtons)
        await message.answer_document(caption=ModerationText.INFO.value.format(
            x=now_deck),
            document=open(Path.DECKS.value + now_deck[3], "rb"),
            reply_markup=kbd)
        await state.set_state(ModerationSM.waiting_for_type.state)
    else:
        await message.answer(ModerationText.INVALID_NUM.value)


async def wait_for_btn(message: types.Message, state: FSMContext):
    # проверка кнопки
    if message.text not in [*ModerationButtons]:
        await message.answer(ModerationText.INVALID_BTN.value)
        return None

    new_type = ""
    if message.text == ModerationButtons.APPROVE.value:
        new_type = DeckTypes.PUBLIC.value
    elif message.text == ModerationButtons.BAN.value:
        new_type = DeckTypes.PRIVATE.value

    data = await state.get_data()
    now_deck = data["decks"][data["ind"]]
    db_obj.change_type_deck(deck_id=now_deck[0],
                            new_type=new_type)
    await state.finish()
    await message.answer(ModerationText.END.value.format(type=new_type),
                         reply_markup=types.ReplyKeyboardRemove())


async def cmd_cancel(message: types.Message, state: FSMContext):
    kbd = types.ReplyKeyboardRemove()
    await state.finish()
    await message.answer(CancelText.CANCEL.value,
                         reply_markup=kbd)


def register_moderation(dp: Dispatcher, db: DBApi, admins: list):
    global db_obj, ADMINS
    db_obj = db
    ADMINS = admins
    dp.register_message_handler(callback=moderation,
                                commands=['moderation'],
                                content_types="text",
                                state="*")
    dp.register_message_handler(callback=cmd_cancel,
                                state=[
                                    ModerationSM.waiting_for_ind,
                                    ModerationSM.waiting_for_type
                                ])
    dp.register_message_handler(callback=wait_for_ind,
                                state=ModerationSM.waiting_for_ind)
    dp.register_message_handler(callback=wait_for_btn,
                                state=ModerationSM.waiting_for_type)
