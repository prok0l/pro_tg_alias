from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from tg_bot.services.db_api import DBApi

db_obj: DBApi = None


class OrderDuration(StatesGroup):
    waiting_for_duration = State()


async def duration_start(message: types.Message, state: FSMContext):
    await message.answer("Напишите длительность раунда в секундах (не больше "
                         "600): ")
    await state.set_state(OrderDuration.waiting_for_duration.state)


async def duration_chosen(message: types.Message, state: FSMContext):
    if message.text.isdigit() and int(message.text) <= 600:
        db_obj.change_duration(tg_id=message.from_user.id,
                               new_duration=int(message.text))
        await state.finish()
        await message.answer("Время изменено")
    else:
        await message.answer("Напишите длительность раунда в секундах"
                             " (не больше 600): ")
        return


async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Действие отменено")


def register_duration(dp: Dispatcher, db: DBApi):
    global db_obj
    db_obj = db
    dp.register_message_handler(callback=duration_start, commands=["duration"],
                                state="*")
    dp.register_message_handler(callback=cmd_cancel, commands=["cancel"],
                                state=OrderDuration.waiting_for_duration)
    dp.register_message_handler(callback=duration_chosen,
                                state=OrderDuration.waiting_for_duration)
