from aiogram import Dispatcher
from aiogram.types import CallbackQuery
from aiogram.utils.exceptions import ChatNotFound

from tgbot.keyboards.main_menu_inline import main_menu_keyboard, menu_button_callback, admin_menu_keyboard
from tgbot.keyboards.referral_menu_inline import referral_keyboard, referral_button_callback
from tgbot.misc.states import User, AdminMenu


async def referral_menu(call: CallbackQuery):
    bot = await call.bot.get_me()
    referral_link = "https://t.me/{bot}?start={id_referral}".format(
        id_referral=call.from_user.id,
        bot=bot.username
    )
    await call.message.edit_text(f"<b>Меню рефералов</b>\n\n"
                                 f"Пригласите человека через вашу"
                                 f" реферальную ссылку и получите <b>100💰на баланс бота</b>\n\n"
                                 f"Ваша реферальная ссылка:\n"
                                 f"{referral_link}",
                                 reply_markup=referral_keyboard,
                                 disable_web_page_preview=True)


async def show_referrals(call: CallbackQuery):
    await call.answer(cache_time=1)
    db = call.bot.get('db')

    referrals = await db.check_referrals(call.from_user.id)
    result = ""

    for num, row in enumerate(referrals):
        try:
            chat = await call.bot.get_chat(row['telegram_id'])
            user_link = chat.get_mention()
            result += str(num + 1) + ". " + user_link + "\n"
        except ChatNotFound:
            user = await db.select_user(telegram_id=int(row['telegram_id']))
            result += str(num + 1) + ". " + str(user['username'] + "\n")

    if result == "":
        await call.message.answer("Похоже что у вас пока нет рефералов❕")
    else:
        await call.message.answer(f"Ваши рефералы💬\n\n"
                                  f"{result}")


async def cancel_referrals(call: CallbackQuery):
    await call.answer(cache_time=1)
    config = call.bot.get('config')
    if call.from_user.id in config.tg_bot.admin_ids:
        await call.message.edit_text("Главное меню📀\n\n"
                                     "<i>режим администратора</i>",
                                     reply_markup=admin_menu_keyboard)
    else:
        await call.message.edit_text(f"Главное меню📀",
                                     reply_markup=main_menu_keyboard)


def register_referral(dp: Dispatcher):
    dp.register_callback_query_handler(referral_menu, menu_button_callback.filter(button="referral"),
                                       state=[User.mainMenu, AdminMenu.adminMenu])
    dp.register_callback_query_handler(show_referrals, referral_button_callback.filter(button="show_referrals"),
                                       state=[User.mainMenu, AdminMenu.adminMenu])
    dp.register_callback_query_handler(cancel_referrals, referral_button_callback.filter(button="cancel_referrals"),
                                       state=[User.mainMenu, AdminMenu.adminMenu])
