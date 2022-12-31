import logging

from aiogram import Dispatcher
from aiogram.utils.exceptions import ChatNotFound


async def error_handler(update, exception):
    if isinstance(exception, ChatNotFound):
        logging.info("No such chat found")
        return True


def register_error_handler(dp: Dispatcher):
    dp.register_errors_handler(error_handler)
