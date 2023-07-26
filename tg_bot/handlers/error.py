import logging

from aiogram import Dispatcher
from aiogram.utils.exceptions import (TelegramAPIError,
                                      MessageNotModified,
                                      CantParseEntities)


async def error_handler(update, exception):
    """
    Exceptions handler. Catches all exceptions within task factory tasks.
    :param update:
    :param exception:
    :return:
    """
    if isinstance(exception, MessageNotModified):
        logging.exception("Сообщение не отредактировано")
        return True

    if isinstance(exception, CantParseEntities):
        logging.exception(f"CantParseEntities: {exception}\n Update: {update}")
        return True

    if isinstance(exception, TelegramAPIError):
        logging.exception(f"TelegramAPIError: {exception}\n Update: {update}")
        return True

    logging.exception(f"Update: {update} \n {exception}")


def register_error(dp: Dispatcher):
    dp.register_errors_handler(callback=error_handler)
