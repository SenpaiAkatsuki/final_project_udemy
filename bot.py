import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from tgbot.config import load_config
from tgbot.filters.admin import AdminFilter
from tgbot.handlers.admin_menu.add_product_inline import product_inline_query
from tgbot.handlers.admin_menu.admin_registration import register_admin
from tgbot.handlers.admin_menu.announcement_handler import register_announcement_handler
from tgbot.handlers.admin_menu.feedback_answer import register_feedback_answer_handler
from tgbot.handlers.admin_menu.feedback_receive import register_feedback_receive_handler
from tgbot.handlers.admin_menu.generate_product import register_inlineMode_handler_admin
from tgbot.handlers.admin_menu.redact_product import redact_product_handlers
from tgbot.handlers.error.error_handler import register_error_handler
from tgbot.handlers.inline_registration import RegistrationInline_handler
from tgbot.handlers.main_menu.feedback import register_feedback_handler
from tgbot.handlers.main_menu.purchase_handler import purchase_handler
from tgbot.handlers.main_menu.referral_menu import register_referral
from tgbot.handlers.user_registration import register_user
from tgbot.integrations.telegraph import TelegraphService
from tgbot.middlewares.environment import EnvironmentMiddleware
from tgbot.middlewares.integration import IntegrationMiddleware
from tgbot.middlewares.throttling import ThrottlingMiddleware
from tgbot.misc.db_api.postgres_db import Database
from tgbot.services.setting_commands import set_default_commands

logger = logging.getLogger(__name__)


def register_all_middlewares(dp, config):
    dp.setup_middleware(EnvironmentMiddleware(config=config))
    dp.setup_middleware(ThrottlingMiddleware())


def register_all_filters(dp):
    dp.filters_factory.bind(AdminFilter)


def register_all_handlers(dp):
    RegistrationInline_handler(dp)
    register_inlineMode_handler_admin(dp)

    register_referral(dp)

    register_feedback_handler(dp)
    register_feedback_receive_handler(dp)
    register_feedback_answer_handler(dp)

    register_announcement_handler(dp)

    purchase_handler(dp)

    register_admin(dp)
    register_user(dp)

    redact_product_handlers(dp)
    product_inline_query(dp)

    register_error_handler(dp)


async def set_all_default_commands(dp: Dispatcher):
    logging.info("Setting default commands")
    await set_default_commands(dp)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")
    config = load_config(".env")

    storage = RedisStorage2(
        host=config.redis.host,
        port=config.redis.port,
    ) if config.tg_bot.use_redis else MemoryStorage()
    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    file_uploader = TelegraphService()
    dp = Dispatcher(bot, storage=storage)
    db = Database()

    dp.middleware.setup(IntegrationMiddleware(file_uploader))

    bot['config'] = config
    bot["file_uploader"] = file_uploader
    bot["db"] = db

    register_all_middlewares(dp, config)
    register_all_filters(dp)
    register_all_handlers(dp)

    await set_all_default_commands(dp)

    await db.create_connection(user=config.db.user,
                               host=config.db.host,
                               password=config.db.password,
                               database=config.db.database)
    await db.create_table_users()
    await db.create_table_products()
    await db.create_table_reports()

    try:
        await dp.start_polling()
    finally:
        await db.close()
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
