from aiogram import types, Dispatcher

from tg_bot.services.db_api import DBApi
from tg_bot.services.consts import MyAccountText, ListDecksTypes
from tg_bot.services.word import word_func

db_obj: DBApi


async def my_account(message: types.Message):
    dur, deck_links, deck_owner, limit, count = \
        db_obj.my_account(tg_id=message.from_user.id)

    # линкованные колоды
    link_decks_lst = []
    for ind in range(len(deck_links[0])):
        name = deck_links[0][ind][1]
        num_words = deck_links[0][ind][2]
        word = word_func(num_words)
        if deck_links[0][ind][0] != deck_links[1]:
            link_decks_lst.append(MyAccountText.LINK_DECKS1.value.
                                  format(name=name, num_words=num_words,
                                         word=word))
        else:
            link_decks_lst.append(MyAccountText.LINK_DECKS2.value.
                                  format(name=name, num_words=num_words,
                                         word=word))

    # созданные колоды
    owner_decks_lst = []
    for ind, (_, name, type_name, num_words) in enumerate(deck_owner):
        word = word_func(num_words)
        type_str = ListDecksTypes.TYPES[type_name]
        owner_decks_lst.append(
            MyAccountText.OWNERS_DECKS.value.format(name=name,
                                                    type_str=type_str,
                                                    num_words=num_words,
                                                    word=word))
    link_decks_str = "\n".join(link_decks_lst)
    owner_decks_str = "\n".join(owner_decks_lst)
    await message.answer(MyAccountText.STR.format(
        dur=dur,
        link_decks_str=link_decks_str,
        owner_decks_str=owner_decks_str,
        count=count,
        limit=limit
    ))


def register_my_account(dp: Dispatcher, db: DBApi):
    global db_obj
    db_obj = db
    dp.register_message_handler(callback=my_account, commands=['my_account'],
                                content_types="text", state=None)
