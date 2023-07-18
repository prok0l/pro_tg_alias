from enum import Enum


class Path(str, Enum):
    decks = "systemd/decks/"


class DeckTypes(str, Enum):
    Public = "Public"
    Private = "Private"
    Moderation = "On moderation"


class DeckTypesList(list, Enum):
    Types = [(DeckTypes.Public, True),
             (DeckTypes.Private, False),
             (DeckTypes.Moderation, False)]


class CancelText(str, Enum):
    CANCEL = "Действие отменено"


class AddDeckButtons(str, Enum):
    YES = "Да"
    NO = "Нет"


class AddDeckText(str, Enum):
    INVALID_ID = "Пожалуйста, после команды укажите id колоды, " \
                 "которую вы хотите добавить"
    NO_ID = "Простите, но колоды с таким id не существует"
    ADDED_EARLIER = "Эта колода уже была добавлена ранее"
    CHECKING_QUESTION = "Вы действительно хотите добавить колоду - {name}"
    INVALID_BTN = "Выберите действие кнопками ниже"
    ADDED = "Колода успешно добавлена"


class MyDecksButtons(str, Enum):
    CHOOSE = "Выбрать"
    DEL = "Удалить"


class MyDecksText(str, Enum):
    START = "Напишите номер колоды из списка: "
    INVALID_NUM = "Пожалуйста, напишите номер из списка"
    CHOOSE_BTN = "Теперь выберите действие"
    INVALID_BTN = "Выберите действие кнопками ниже"
    CHOOSE_DECK = "Вы выбрали колоду - {name}"
    DEL_DECK = "Колода успешно удалена"


class NewDeckText(str, Enum):
    MAX_DECKS = "У вас максимальное количество колод"
    NAME = "Напишите название новой колоды:  "
    BUZY = "Извините, это название уже занято"
    TXT = "Теперь пришлите файл с расширением txt"
    ADDED = "Добавлена колода - {name}\n"\
            "Статус {type} "\
            "можно изменить в меню колод.\n"\
            "id колоды - <code>{deck_id}</code>"


class DurationText(str, Enum):
    START = "Напишите длительность раунда в секундах (не больше 600): "
    EDIT = "Время изменено"
    INVALID_TIME = "Напишите длительность раунда в секундах (не больше 600): "


class Start(str, Enum):
    START = "Привет, я telegram bot для игры в <b>Alias</b>, " \
            "с возможностью создания собственной колоды.\n\n" \
            "Разработчик уведомляет, что вся ответственность с " \
            "момента начала использования данного программного " \
            "продукта за содержание загруженных файлов несёт " \
            "пользователь программы."


class Help(str, Enum):
    LIST = "Список команд:\n"
    START = "/start - старт бота\n"
    HELP = "/help - список команд\n"
    NEW_GAME = "/new_game - запустить игру\n"
    STOP_GAME = "/stop_game - остановить игру\n"
    ADD_DECK = "/add_deck - добавить колоду через id\n"
    DURATION = "/duration - длительность раунда\n"
    MY_DECKS = "/my_decks - список колод\n"
    NEW_DECK = "/new_deck - создать свою колоду\n"
    CANCEL = "/cancel - отменить операцию\n"
    DECKS_SHOP = "/decks_shop - магазин колод\n"


class DecksShopText(str, Enum):
    START = "Напишите номер колоды из списка: "
    INVALID_NUM = "Пожалуйста, напишите номер из списка"
    ADD_DECK = "Колода успешно добавлена"
    ADDED_EARLIER = "Эта колода уже была добавлена ранее"
