import os

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from tg_bot.services.db_api import DBApi
from tg_bot.services.consts import CancelText, ListDecksTypes, ListDecksText,\
    ListDecksButtons, DeckTypes, Path
from tg_bot.services.file_filter import file_filter

db_obj: DBApi


class ListDecksSM(StatesGroup):
    waiting_for_ind = State()
    waiting_for_btn_action = State()
    waiting_for_btn_edit = State()
    waiting_for_btn_delete = State()
    waiting_for_new_name = State()
    waiting_for_new_path = State()
    waiting_for_type = State()


async def list_decks_start(message: types.Message, state: FSMContext):
    decks = db_obj.decks_by_owner(tg_id=message.from_user.id)
    if not decks:
        await message.answer(ListDecksText.NO_DECKS.value)
        return None
    decks_str_lst = []
    for ind, (_, name, type_name) in enumerate(decks):
        type_str = ListDecksTypes.TYPES[type_name]
        decks_str_lst.append(
            ListDecksText.LIST.value.format(ind=ind + 1, name=name,
                                            type_str=type_str))

    await message.answer(ListDecksText.YOUR_DECKS.value +
                         "\n".join(decks_str_lst) + "\n" +
                         ListDecksText.START.value)
    await state.update_data(decks=decks)
    await state.set_state(ListDecksSM.waiting_for_ind.state)


async def deck_chosen(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if message.text.isdigit() and\
            0 < (ind := int(message.text)) <= len(data["decks"]):
        await state.update_data(ind=ind - 1)
        await state.set_state(ListDecksSM.waiting_for_btn_action.state)
        kbd = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kbd.add(*ListDecksButtons.Actions)
        await message.answer(ListDecksText.CHOOSE_BTN.value,
                             reply_markup=kbd)
    else:
        await message.answer(ListDecksText.INVALID_NUM.value)


async def action_btn(message: types.Message, state: FSMContext):
    if message.text not in [*ListDecksButtons.Actions]:
        await message.answer(ListDecksText.INVALID_BTN.value)
        return None
    kbd = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if message.text == ListDecksButtons.Actions.EDIT.value:
        kbd.add(*ListDecksButtons.Edit)
        await message.answer(ListDecksText.ACTION_EDIT.value,
                             reply_markup=kbd)
        await state.set_state(ListDecksSM.waiting_for_btn_edit.state)
    elif message.text == ListDecksButtons.Actions.DEL.value:
        kbd.add(*ListDecksButtons.Delete)
        await message.answer(ListDecksText.ACTION_EDIT.value,
                             reply_markup=kbd)
        await state.set_state(ListDecksSM.waiting_for_btn_delete.state)
    elif message.text == ListDecksButtons.Actions.TYPE.value:
        data = await state.get_data()
        deck = data["decks"][data["ind"]]
        msg = ""
        if deck[2] == DeckTypes.PRIVATE.value:
            msg = ListDecksText.TYPE_PRIVATE.value
        elif deck[2] == DeckTypes.MODERATION.value:
            msg = ListDecksText.TYPE_MODERATION.value
        elif deck[2] == DeckTypes.PUBLIC.value:
            msg = ListDecksText.TYPE_PUBLIC.value
        kbd.add(*ListDecksButtons.Type)
        await message.answer(msg, reply_markup=kbd)
        await state.set_state(ListDecksSM.waiting_for_type.state)


async def edit_btn(message: types.Message, state: FSMContext):
    if message.text not in [*ListDecksButtons.Edit]:
        await message.answer(ListDecksText.INVALID_BTN.value)
        return None
    kbd = types.ReplyKeyboardRemove()
    if message.text == ListDecksButtons.Edit.NAME.value:
        await state.set_state(ListDecksSM.waiting_for_new_name.state)
        await message.answer(ListDecksText.NEW_NAME.value, reply_markup=kbd)

    elif message.text == ListDecksButtons.Edit.FILE.value:
        await state.set_state(ListDecksSM.waiting_for_new_path.state)
        await message.answer(ListDecksText.NEW_FILE.value, reply_markup=kbd)


async def del_btn(message: types.Message, state: FSMContext):
    if message.text not in [*ListDecksButtons.Delete]:
        await message.answer(ListDecksText.INVALID_BTN.value)
        return None
    if message.text == ListDecksButtons.Delete.YES.value:
        data = await state.get_data()
        deck = data["decks"][data["ind"]]
        db_obj.del_deck(deck_id=deck[0])
        await message.answer(ListDecksText.DELETE.value,
                             reply_markup=types.ReplyKeyboardRemove())
        await state.finish()
    elif message.text == ListDecksButtons.Delete.NO.value:
        await cmd_cancel(message=message, state=state)


async def new_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    deck = data["decks"][data["ind"]][0]
    is_new_name = db_obj.rename_deck(deck_id=deck,
                                     new_name=message.text)
    if not is_new_name:
        await message.answer(ListDecksText.BUZY.value)
    else:
        await message.answer(ListDecksText.RENAME.value)
        await state.finish()


async def new_path(message: types.Message, state: FSMContext):
    data = await state.get_data()
    deck = data["decks"][data["ind"]][0]
    file = await message.bot.get_file(message.document.file_id)
    path = str(max(int(x.split(".")[0]) for x in os.listdir(Path.DECKS.value +
                                                            '.')) + 1) + ".txt"
    await message.bot.download_file(file_path=file.file_path,
                                    destination=Path.DECKS.value + path)
    file_filter(Path.DECKS.value + path)
    db_obj.change_file_in_deck(deck_id=deck,
                               new_path=path)


async def type_order(message: types.Message, state: FSMContext):
    if message.text not in [*ListDecksButtons.Type]:
        await message.answer(ListDecksText.INVALID_BTN.value)
        return None
    if message.text == ListDecksButtons.Type.NO.value:
        await cmd_cancel(message=message, state=state)
        return None
    data = await state.get_data()
    deck = data["decks"][data["ind"]]
    kbd = types.ReplyKeyboardRemove()
    if deck[2] == DeckTypes.PRIVATE.value:
        db_obj.change_type_deck(deck_id=deck[0],
                                new_type=DeckTypes.MODERATION.value)
        await message.answer(ListDecksText.TYPE_EDIT.value, reply_markup=kbd)
    elif deck[2] == DeckTypes.MODERATION.value:
        db_obj.change_type_deck(deck_id=deck[0],
                                new_type=DeckTypes.PRIVATE.value)
        await message.answer(ListDecksText.TYPE_EDIT_PRIVATE.value,
                             reply_markup=kbd)
    elif deck[2] == DeckTypes.PUBLIC.value:
        db_obj.change_type_deck(deck_id=deck[0],
                                new_type=DeckTypes.PRIVATE.value)
        await message.answer(ListDecksText.TYPE_EDIT_PRIVATE.value,
                             reply_markup=kbd)
    await state.finish()


async def cmd_cancel(message: types.Message, state: FSMContext):
    kbd = types.ReplyKeyboardRemove()
    await state.finish()
    await message.answer(CancelText.CANCEL.value,
                         reply_markup=kbd)


def register_list_decks(dp: Dispatcher, db: DBApi):
    global db_obj
    db_obj = db
    dp.register_message_handler(callback=list_decks_start,
                                commands=["list_decks"],
                                state="*")
    dp.register_message_handler(callback=cmd_cancel, commands=["cancel"],
                                state=[
                                    ListDecksSM.waiting_for_ind,
                                    ListDecksSM.waiting_for_btn_action,
                                    ListDecksSM.waiting_for_btn_edit,
                                    ListDecksSM.waiting_for_btn_delete,
                                    ListDecksSM.waiting_for_new_name,
                                    ListDecksSM.waiting_for_new_path,
                                    ListDecksSM.waiting_for_type
                                ])
    dp.register_message_handler(callback=deck_chosen,
                                state=ListDecksSM.waiting_for_ind)
    dp.register_message_handler(callback=action_btn,
                                state=ListDecksSM.waiting_for_btn_action)
    dp.register_message_handler(callback=edit_btn,
                                state=ListDecksSM.waiting_for_btn_edit)
    dp.register_message_handler(callback=del_btn,
                                state=ListDecksSM.waiting_for_btn_delete)
    dp.register_message_handler(callback=new_name,
                                state=ListDecksSM.waiting_for_new_name)
    dp.register_message_handler(callback=new_path,
                                state=ListDecksSM.waiting_for_new_path,
                                content_types=types.ContentType.DOCUMENT)
    dp.register_message_handler(callback=type_order,
                                state=ListDecksSM.waiting_for_type)
