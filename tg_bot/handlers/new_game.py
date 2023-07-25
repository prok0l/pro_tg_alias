import random
import time
from asyncio import sleep
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

from tg_bot.services.db_api import DBApi
from tg_bot.services.consts import Path, NewGameText, NewGameButtons

user_data = {}
db_obj: DBApi = None


class GameSM(StatesGroup):
    now_game = State()


def word_func(count: int) -> str:
    """
    Функция для склонения слова "слово"
    :param count:
    :return:
    """
    if count != 11 and count % 10 == 1:
        return NewGameText.WORD1.value  # слово
    elif 10 < count < 20 or 4 < count % 10 or count % 10 == 0:
        return NewGameText.WORD2.value  # слов
    else:
        return NewGameText.WORD3.value  # слова


def generate_string(data: dict) -> str:
    return NewGameText.START.value.format(time=data['now_time'],
                                          words="\n".join(data["now_list"]))


async def bot_new_game(message: types.Message, state: FSMContext):
    id_user = message.from_user.id
    # проверка на идущую игру (аля Singleton)
    if user_data.get(id_user, {"is_now_game": False})["is_now_game"]:
        await message.delete()
        return None

    # получение настроек игры
    duration, path = db_obj.user_info(id_user)

    if not path:
        await message.answer(NewGameText.NO_AVAILABLE_DECK.value)
        return None

    # генерация колоды
    with open(Path.DECKS.value + path,
              encoding="utf-8") as f:
        list_words = [x.strip() for x in f.readlines()]
    random.shuffle(list_words)

    # генерация настроек
    user_data[id_user] = {"now_list": [],
                          "deck": list_words,
                          "true_count": 0,
                          "skip_count": 0,
                          "is_now_game": True,
                          "now_time": duration,
                          "last_click": time.time() * 1000}

    data = user_data[id_user]
    data["now_list"].append(data["deck"][0])

    # создание клавиатуры
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(
        text=NewGameButtons.TRUE.value,
        callback_data=NewGameButtons.TRUE.name.lower()
    ))
    keyboard.insert(types.InlineKeyboardButton(
        text=NewGameButtons.SKIP.value,
        callback_data=NewGameButtons.SKIP.name.lower()
    ))
    data["kbd"] = keyboard

    my_msg = await message.answer(generate_string(data),
                                  reply_markup=data["kbd"])
    await state.set_state(GameSM.now_game.state)

    # игра (изменение времени)
    while data["now_time"] > 0:
        await sleep(1)

        # обработка стоп
        if not data["is_now_game"]:
            data["now_time"] = 1

        data["now_time"] -= 1
        await my_msg.edit_text(generate_string(data),
                               reply_markup=data["kbd"])

    data["is_now_game"] = False
    await state.finish()
    await sleep(0.1)
    # обработка конца игры
    await my_msg.edit_text(NewGameText.END.value.format(
        words="\n".join(data["now_list"]),
        true_count=data["true_count"],
        true_word=word_func(data["true_count"]),
        skip_count=data["skip_count"],
        skip_word=word_func(data["skip_count"])
    ))


async def bot_stop_game(message: types.Message):
    if message.from_user.id not in user_data.keys():
        return None
    user_data[message.from_user.id]["is_now_game"] = False


async def send_reaction(call: types.CallbackQuery):
    # проверка на запущенную игру
    if call.from_user.id not in user_data.keys():
        return None

    data = user_data[call.from_user.id]

    # тайм аут кликов (для защиты от дабл клика)
    now_time = time.time() * 1000
    if now_time - data["last_click"] < 600:
        return None
    data["last_click"] = now_time
    await call.answer()

    # проверка на конец колоды
    if data["true_count"] + data["skip_count"] >= len(data["deck"]):
        data["is_now_game"] = False
        return None

    # обработка кнопки (Угадали)
    if call.data == NewGameButtons.TRUE.name.lower():
        data["now_list"][-1] = NewGameText.TRUE_WORD.value.format(
            word=data["now_list"][-1]
        )
        data["true_count"] += 1
    # обработка кнопки (Пропустить)
    else:
        data["now_list"][-1] = NewGameText.SKIP_WORD.value.format(
            word=data["now_list"][-1]
        )
        data["skip_count"] += 1

    # измененение строки сообщения
    if data["true_count"] + data["skip_count"] < len(data["deck"]):
        data["now_list"].append(data["deck"][data["true_count"] +
                                             data["skip_count"]])
        await call.message.edit_text(generate_string(data),
                                     reply_markup=data["kbd"])


def register_new_game(dp: Dispatcher, db: DBApi):
    global db_obj
    db_obj = db
    dp.register_message_handler(callback=bot_new_game, commands=['new_game'],
                                content_types="text", state=None)
    dp.register_message_handler(callback=bot_stop_game, commands=['stop_game'],
                                content_types="text", state=None)
    dp.register_callback_query_handler(callback=send_reaction,
                                       state=GameSM.now_game)
