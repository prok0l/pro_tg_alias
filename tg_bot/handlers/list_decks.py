from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from tg_bot.services.db_api import DBApi
from tg_bot.services.consts import CancelText, ListDecksTypes, ListDecksText,\
    ListDecksButtons, DeckTypes

db_obj: DBApi = None


class ListDecksSM(StatesGroup):
    waiting_for_ind = State()
    waiting_for_btn_action = State()
    waiting_for_btn_edit = State()
    waiting_for_btn_delete = State()
    waiting_for_new_name = State()
    waiting_for_new_path = State()


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
    else:
        kbd.add(*ListDecksButtons.Delete)
        await message.answer(ListDecksText.ACTION_EDIT.value,
                             reply_markup=kbd)
        await state.set_state(ListDecksSM.waiting_for_btn_delete.state)


async def edit_btn(message: types.Message, state: FSMContext):
    if message.text not in [*ListDecksButtons.Edit]:
        await message.answer(ListDecksText.INVALID_BTN.value)
        return None
    kbd = types.ReplyKeyboardRemove()
    if message.text == ListDecksButtons.Edit.NAME.value:
        await state.set_state(ListDecksSM.waiting_for_new_name.state)
        await message.answer(ListDecksText.NEW_NAME.value, reply_markup=kbd)

    if message.text == ListDecksButtons.Edit.FILE.value:
        await state.set_state(ListDecksSM.waiting_for_new_path.state)
        await message.answer(ListDecksText.NEW_FILE.value, reply_markup=kbd)

    if message.text == ListDecksButtons.Edit.TYPE.value:
        data = await state.get_data()
        deck = data["decks"][data["ind"]][0]
        db_obj.change_type_deck(deck_id=deck,
                                new_type=DeckTypes.MODERATION.value)
        await message.answer(ListDecksText.TYPE_EDIT.value,
                             reply_markup=kbd)
        await state.finish()


async def del_btn(message: types.Message, state: FSMContext):
    if message.text not in [*ListDecksButtons.Delete]:
        await message.answer(ListDecksText.INVALID_BTN.value)
        return None
    if message.text == ListDecksButtons.Delete.YES.value:
        pass
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
    pass


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