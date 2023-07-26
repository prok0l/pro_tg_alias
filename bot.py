import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from tg_bot.config import load_config
from tg_bot.handlers.help import register_help
from tg_bot.handlers.my_decks import register_my_decks
from tg_bot.handlers.new_deck import register_new_deck
from tg_bot.handlers.new_game import register_new_game
from tg_bot.handlers.start import register_start
from tg_bot.handlers.duration import register_duration
from tg_bot.handlers.add_deck import register_add_deck
from tg_bot.handlers.decks_shop import register_decks_shop
from tg_bot.handlers.list_decks import register_list_decks
from tg_bot.handlers.my_account import register_my_account
from tg_bot.handlers.change_limit import register_change_limit
from tg_bot.handlers.users import register_users
from tg_bot.handlers.moderation import register_moderation
from tg_bot.handlers.error import register_error
from tg_bot.services.db_api import DBApi

logger = logging.getLogger(__name__)


def register_all_middlewares(dp):
    # dp.setup_middleware(...)
    pass


def register_all_filters(dp):
    # dp.filters_factory.bind(...)
    pass


def register_all_handlers(dp: Dispatcher, db: DBApi, admins: list):
    register_start(dp=dp, db=db)
    register_help(dp=dp)
    register_new_game(dp=dp, db=db)
    register_duration(dp=dp, db=db)
    register_new_deck(dp=dp, db=db)
    register_add_deck(dp=dp, db=db)
    register_my_decks(dp=dp, db=db)
    register_decks_shop(dp=dp, db=db)
    register_list_decks(dp=dp, db=db)
    register_my_account(dp=dp, db=db)
    register_users(dp=dp, db=db, admins=admins)
    register_change_limit(dp=dp, db=db, admins=admins)
    register_moderation(dp=dp, db=db, admins=admins)
    register_error(dp)


async def main():
    logging.basicConfig(level=logging.INFO,
                        format=u'%(filename)s:%(lineno)d #%(levelname)-8s'
                               u' [%(asctime)s] - %(name)s - %(message)s')

    config = load_config(".env")
    bot = Bot(token=config.token, parse_mode="HTML")
    storage = RedisStorage2() if config.use_redis else MemoryStorage()
    dp = Dispatcher(bot, storage=storage)
    bot['config'] = config
    db = DBApi("systemd/1.db")
    register_all_middlewares(dp)
    register_all_filters(dp)
    register_all_handlers(dp=dp, db=db, admins=config.admin_ids)

    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.wait_closed()
        session = await bot.get_session()
        await session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main=main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("BOT STOPPED!!!")
