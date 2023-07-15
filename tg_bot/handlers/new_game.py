import random
import time
from asyncio import sleep
from aiogram import types, Dispatcher

from tg_bot.services.db_api import DBApi
from tg_bot.services.consts import Path

user_data = {}
db_obj = None


def word(count: int) -> str:
    """
    Функция для склонения слова "слово"
    :param count:
    :return:
    """
    if count != 11 and count % 10 == 1:
        return "слово"
    elif 10 < count < 20 or 4 < count % 10 or count % 10 == 0:
        return "слов"
    else:
        return "слова"


def generate_string(data: dict) -> str:
    time_str = f"Время: {data['now_time']} ⏱\n"
    return time_str + "Слова:\n" + "\n".join(data["now_list"])


async def bot_new_game(message: types.Message):
    id_user = message.from_user.id
    if user_data.get(id_user, {"is_now_game": False})["is_now_game"]:
        await message.delete()
        return None
    duration, path = db_obj.user_info(id_user)
    with open(Path.decks.value + path,
              encoding="utf-8") as f:
        list_words = [x.strip() for x in f.readlines()]
    random.shuffle(list_words)
    user_data[id_user] = {"now_list": [],
                          "deck": list_words,
                          "true_count": 0,
                          "skip_count": 0,
                          "is_now_game": True,
                          "now_time": duration,
                          "last_click": time.time() * 1000}
    data = user_data[id_user]
    data["now_list"].append(data["deck"][0])
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Угадали",
                                            callback_data="true"))
    keyboard.insert(types.InlineKeyboardButton(text="Пропустить",
                                               callback_data="skip"))
    data["kbd"] = keyboard
    my_msg = await message.answer(generate_string(data),
                                  reply_markup=data["kbd"])

    while data["now_time"] > 0:
        await sleep(1)
        if not data["is_now_game"]:
            data["now_time"] = 1
        data["now_time"] -= 1
        await my_msg.edit_text(generate_string(data),
                               reply_markup=data["kbd"])

    true_count = data["true_count"]
    skip_count = data["skip_count"]
    await my_msg.edit_text("Время вышло ⏱\n" +
                           "\n".join(data["now_list"]) + "\n"
                           f"Вы угадали {true_count} {word(true_count)}\n"
                           f"Вы пропустили {skip_count} {word(skip_count)}")
    data["is_now_game"] = False


async def bot_stop_game(message: types.Message):
    if message.from_user.id not in user_data.keys():
        return None
    user_data[message.from_user.id]["is_now_game"] = False


async def send_reaction(call: types.CallbackQuery):
    if call.from_user.id not in user_data.keys():
        return None
    data = user_data[call.from_user.id]
    now_time = time.time() * 1000
    if now_time - data["last_click"] < 600:
        return None
    data["last_click"] = now_time
    await call.answer()
    if data["true_count"] + data["skip_count"] >= len(data["deck"]):
        data["is_now_game"] = False
        return None
    if call.data == "true":
        data["now_list"][-1] += " ✅"
        data["true_count"] += 1
    else:
        data["now_list"][-1] = f"<s>{data['now_list'][-1]}</s>"
        data["skip_count"] += 1
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
    dp.register_callback_query_handler(callback=send_reaction)
