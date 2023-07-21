from aiogram import types, Dispatcher

from tg_bot.services.db_api import DBApi
from tg_bot.services.consts import MyAccountText, ListDecksTypes

db_obj: DBApi = None


async def my_account(message: types.Message):
    dur, deck_links, deck_owner, limit, count = \
        db_obj.my_account(tg_id=message.from_user.id)
    link_decks_lst = []
    for ind in range(len(deck_links[0])):
        if deck_links[0][ind][0] != deck_links[1]:
            link_decks_lst.append(MyAccountText.LINK_DECKS1.value.
                                  format(name=deck_links[0][ind][1]))
        else:
            link_decks_lst.append(MyAccountText.LINK_DECKS2.value.
                                  format(name=deck_links[0][ind][1]))
    owner_decks_lst = []
    for ind, (_, name, type_name) in enumerate(deck_owner):
        type_str = ListDecksTypes.TYPES[type_name]
        owner_decks_lst.append(
            MyAccountText.OWNERS_DECKS.value.format(name=name,
                                                    type_str=type_str))
    link_decks_str = "\n".join(link_decks_lst)
    owner_decks_str = "\n".join(owner_decks_lst)
    await message.answer(f"{MyAccountText.DURATION.value} {dur}\n"
                         f"{MyAccountText.LINK_DECKS_STR.value}"
                         f"{link_decks_str}\n"
                         f"{MyAccountText.OWNERS_DECKS_STR.value}"
                         f"{owner_decks_str}\n"
                         f"{MyAccountText.LIMIT.value} {count}/{limit}")


def register_my_account(dp: Dispatcher, db: DBApi):
    global db_obj
    db_obj = db
    dp.register_message_handler(callback=my_account, commands=['my_account'],
                                content_types="text", state=None)
