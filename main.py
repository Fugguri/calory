import sys
import openai
import asyncio
import logging
from db.MySql import Database
# from db.sqlite_connection import Database

from config.config import load_config

from keyboards.keyboards import Keyboards

from handlers.users import register_user_handlers
from handlers.admin import register_admin_handlers
from handlers.education import register_education_handlers

from middlewares.environment import EnvironmentMiddleware
from middlewares import SubscriptionMiddleware

from aiogram import Bot, Dispatcher, utils
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from utils.mailingServices import Message_scheduler
logger = logging.getLogger(__name__)


async def register_all_middlewares(dp, config, keyboards, db, openai, bot, ):

    dp.middleware.setup(EnvironmentMiddleware(
        config=config, db=db, keyboards=keyboards, openai=openai, bot=bot))
    dp.middleware.setup(SubscriptionMiddleware())


def register_all_handlers(dp, keyboards):
    register_admin_handlers(dp, keyboards)
    register_user_handlers(dp, keyboards)
    register_education_handlers(dp, keyboards)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
        # filename="logs.log"
    )
    print("Starting bot")
    logger.info("Starting bot")

    config = load_config("config/config.json", "config/texts.yml")
    storage = MemoryStorage()

    openai.api_key = config.tg_bot.openai
    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    db = Database(cfg=config)
    dp = Dispatcher(bot, storage=storage)
    db.cbdt()
    kbs = Keyboards(config)
    ms = Message_scheduler(bot=bot, keyboards=kbs)

    bot['keyboards'] = kbs
    bot['config'] = config

    await register_all_middlewares(dp, config, kbs, db, openai, bot)

    register_all_handlers(dp, kbs)
    await ms.start_scheduler()

    # start
    dp.skip_updates = False
    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        session = await bot.get_session()
        await session.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
    except utils.exceptions.TerminatedByOtherGetUpdates:
        sys.exit()
