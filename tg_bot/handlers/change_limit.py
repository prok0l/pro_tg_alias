from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from tg_bot.services.db_api import DBApi
from tg_bot.services.consts import CancelText, ChangeLimitText

db_obj: DBApi
ADMINS: list


class ChangeLimitSM(StatesGroup):
    waiting_for_limit = State()


async def change_limit(message: types.Message, state: FSMContext):
    # проверка что сообщение от админа
    if message.from_user.id not in ADMINS:
        return None

    tg_id = message.get_args()
    # проверка на существование юзера
    if not tg_id or not db_obj.check_user_in_db(tg_id=tg_id):
        await message.answer(ChangeLimitText.NO_USER.value)
        return None
    await state.update_data(tg_id=tg_id)
    await state.set_state(ChangeLimitSM.waiting_for_limit.state)
    await message.answer(ChangeLimitText.WAIT_LIMIT.value)


async def set_limit(message: types.Message, state: FSMContext):
    # проверка что введенное значение число
    if set(message.text) <= set(ChangeLimitText.ALPH.value):
        data = await state.get_data()
        db_obj.change_limit(tg_id=data["tg_id"],
                            new_limit=message.text)
        await message.answer(ChangeLimitText.NEW_LIMIT.value)
        await state.finish()
    else:
        await message.answer(ChangeLimitText.INCORRECT.value)


async def cmd_cancel(message: types.Message, state: FSMContext):
    kbd = types.ReplyKeyboardRemove()
    await state.finish()
    await message.answer(CancelText.CANCEL.value,
                         reply_markup=kbd)


def register_change_limit(dp: Dispatcher, db: DBApi, admins: list):
    global db_obj, ADMINS
    db_obj = db
    ADMINS = admins
    dp.register_message_handler(callback=change_limit,
                                commands=['change_limit'],
                                content_types="text", state=None)
    dp.register_message_handler(callback=cmd_cancel,
                                state=ChangeLimitSM.waiting_for_limit,
                                commands=['cancel'])
    dp.register_message_handler(callback=set_limit,
                                state=ChangeLimitSM.waiting_for_limit)
