from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from asyncpg import UniqueViolationError

from tgbot.keyboards.admin_inline import admin_panel_buttons, admin_panel_callback
from tgbot.keyboards.main_menu_inline import admin_menu_keyboard
from tgbot.misc.rate_limit import rate_limit
from tgbot.misc.states import User, AdminMenu


@rate_limit(2)
async def admin_start(message: Message):
    db = message.bot.get('db')
    try:
        await db.add_user(telegram_id=message.from_user.id,
                          username=message.from_user.username)
        await db.change_user_balance(99999, message.from_user.id)
    except UniqueViolationError:
        pass

    await message.reply("Добро пожаловать <b>Админ</b>📀",
                        reply_markup=admin_menu_keyboard)
    await AdminMenu.adminMenu.set()


async def admin_panel(call: CallbackQuery):
    await call.message.edit_text("<b>Меню администратора📀</b>\n\n"
                                 "<i>режим администратора</i>",
                                 reply_markup=admin_panel_buttons)
    await AdminMenu.adminMenu.set()


async def return_to_user_mode(call: CallbackQuery):
    await call.message.edit_text("<b>Меню пользователя📀</b>\n\n"
                                 "<i>режим администратора</i>",
                                 reply_markup=admin_menu_keyboard)

    await User.mainMenu.set()


def register_admin(dp: Dispatcher):
    dp.register_message_handler(admin_start, commands=["start"], is_admin=True)
    dp.register_callback_query_handler(admin_panel, admin_panel_callback.filter(button="admin_panel"),
                                       state="*")
    dp.register_callback_query_handler(return_to_user_mode, admin_panel_callback.filter(button="return_to_user"),
                                       state=AdminMenu.adminMenu)
