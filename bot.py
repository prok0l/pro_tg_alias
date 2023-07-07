import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from tg_bot.config import load_config
from tg_bot.handlers.help import register_help
from tg_bot.handlers.new_game import register_new_game
from tg_bot.handlers.start import register_start
from tg_bot.handlers.error import register_error
from tg_bot.services.db_api import DBApi

logger = logging.getLogger(__name__)


def register_all_middlewares(dp):
    # dp.setup_middleware(...)
    pass


def register_all_filters(dp):
    # dp.filters_factory.bind(...)
    pass


def register_all_handlers(dp, db):
    register_start(dp, db)
    register_help(dp)
    register_new_game(dp, db)
    register_error(dp)


async def main():
    logging.basicConfig(level=logging.INFO,
                        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s')

    config = load_config(".env")
    bot = Bot(token=config.token, parse_mode="HTML")
    storage = RedisStorage2() if config.use_redis else MemoryStorage()
    dp = Dispatcher(bot, storage=storage)
    bot['config'] = config
    db = DBApi("systemd/1.db")
    register_all_middlewares(dp)
    register_all_filters(dp)
    register_all_handlers(dp, db)

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
