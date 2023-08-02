from tg_bot.services.consts import NewGameText


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
