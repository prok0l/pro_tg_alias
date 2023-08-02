from enum import Enum


class Path(str, Enum):
    DECKS = "systemd/decks/"


class DeckTypes(str, Enum):
    PUBLIC = "Public"
    PRIVATE = "Private"
    MODERATION = "On moderation"


class DeckTypesList(list, Enum):
    Types = [(DeckTypes.PUBLIC, True),
             (DeckTypes.PRIVATE, False),
             (DeckTypes.MODERATION, False)]


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
    CHECKING_QUESTION = "Вы действительно хотите добавить колоду - {name}\t" \
                        "({num_words} {word})"
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
    NO_DECKS = "У вас нету колод"
    DECK_NAME = "{ind}) {name}\t({num_words} {word})"
    DECK_NAME_USED = "{ind}) <b>{name}</b>\t({num_words} {word})"


class NewDeckText(str, Enum):
    MAX_DECKS = "У вас максимальное количество колод"
    NAME = "Напишите название новой колоды:  "
    BUZY = "Извините, это название уже занято"
    TXT = "Теперь пришлите файл с расширением txt"
    ADDED = "Добавлена колода - {name}\n" \
            "Статус {type} " \
            "можно изменить в меню колод.\n" \
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
    DECKS_SHOP = "/decks_shop - магазин колод\n"
    LIST_DECKS = "/list_decks - колоды созданные мной\n"
    MY_ACCOUNT = "/my_account - информация об аккаунте\n"
    CANCEL = "/cancel - отменить операцию\n"


class AdminHelp(str, Enum):
    USERS = "/users - список юзеров\n"
    CHANGE_LIMIT = "/change_limit `tg_id` - смена лимита\n"
    MODERATION = "/moderation - модерация колод\n"


class DecksShopText(str, Enum):
    START = MyDecksText.START.value
    INVALID_NUM = MyDecksText.INVALID_NUM.value
    ADD_DECK = AddDeckText.ADDED.value
    ADDED_EARLIER = AddDeckText.ADDED_EARLIER.value
    DECK_NAME = "{ind}) {name}\t({num_words} {word})"
    DECK_NAME_AVAILABLE = "{ind}) <s>{name} \t({num_words} {word})</s>"


class ListDecksTypes(dict, Enum):
    TYPES = {
        DeckTypes.PUBLIC.value: "🔓",
        DeckTypes.PRIVATE.value: "🔒",
        DeckTypes.MODERATION.value: "⌛️"
    }


class ListDecksText(str, Enum):
    LIST = "{ind}) {name}\t({num_words} {word})\t{type_str}"
    YOUR_DECKS = "Колоды созданные вами:\n"
    INVALID_NUM = MyDecksText.INVALID_NUM.value
    START = MyDecksText.START.value
    CHOOSE_BTN = MyDecksText.CHOOSE_BTN.value
    INVALID_BTN = MyDecksText.INVALID_BTN.value
    ACTION_EDIT = "Теперь выберите действие"
    TYPE_EDIT = "Колода отправлена на проверку"
    NEW_NAME = "Введите новое название для колоды: "
    NEW_FILE = "Отправьте новый файл для колоды с расширением txt"
    NO_DECKS = "Вы ещё не создали, ни одной колоды"
    BUZY = NewDeckText.BUZY.value
    RENAME = "Имя успешно изменено"
    TYPE_PRIVATE = "Отправить на модерацию"
    TYPE_MODERATION = "Сделать приватной"
    TYPE_PUBLIC = "Сделать приватной"
    TYPE_EDIT_PRIVATE = "Колода сделана приватной"
    DELETE = "Колода успешно удалена"
    NEW_FILE_ADD = "Файл успешно изменен"


class ListDecksButtons:
    class Actions(str, Enum):
        EDIT = "Изменить"
        DEL = "Удалить"
        TYPE = "Статус"

    class Delete(str, Enum):
        YES = "Да"
        NO = "Нет"

    class Edit(str, Enum):
        NAME = "Название"
        FILE = "Файл"

    class Type(str, Enum):
        YES = "Да"
        NO = "Нет"


class LimitText(str, Enum):
    UNLIMIT = "♾️"


class MyAccountText(str, Enum):
    LINK_DECKS1 = "{name}\t({num_words} {word})"
    LINK_DECKS2 = "<b>{name}</b>\t({num_words} {word})"
    OWNERS_DECKS = "{name}\t{type_str}\t({num_words} {word})"
    STR = "Длительность раунда: {dur} сек.\n" + \
          "Мои колоды:\n" + \
          "{link_decks_str}\n" + \
          "Колоды созданные мной:\n" + \
          "{owner_decks_str}\n" + \
          "Лимит: {count}/{limit}"


class NewGameText(str, Enum):
    WORD1 = "слово"
    WORD2 = "слов"
    WORD3 = "слова"
    START = "Время: {time} ⏱\n" \
            "Слова:\n" \
            "{words}"
    NO_AVAILABLE_DECK = "Простите, но у вас нету выбранной колоды для игры"
    END = "Время вышло ⏱\n" \
          "{words}\n" \
          "Вы угадали {true_count} {true_word}\n" \
          "Вы пропустили {skip_count} {skip_word}"
    TRUE_WORD = "{word} ✅"
    SKIP_WORD = "<s>{word}</s>"


class NewGameButtons(str, Enum):
    TRUE = "Угадали"
    SKIP = "Пропустить"


class ChangeLimitText(str, Enum):
    NO_USER = "Извините, но такого юзера не обнаружено"
    WAIT_LIMIT = "Теперь введите лимит для данного пользователя"
    ALPH = "-0123456789"
    NEW_LIMIT = "Лимит успешно изменен"
    INCORRECT = "Пожалуйста напишите лимит цифрами"


class ModerationText(str, Enum):
    NO_DECKS = "Нет колод на модерации"
    START = "{ind}) {x[1]}\t({x[2]})"
    START_FULL = "{str}\n" + MyDecksText.START.value
    INVALID_NUM = MyDecksText.INVALID_NUM.value
    INFO = "name: {x[1]}\n" \
           "owner: {x[2]}\n" \
           "num_words: {x[4]}"
    INVALID_BTN = MyDecksText.INVALID_BTN.value
    END = "Тип колоды изменен на: {type}"


class ModerationButtons(str, Enum):
    APPROVE = "Одобрить"
    BAN = "Запретить"
