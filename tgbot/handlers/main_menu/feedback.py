from aiogram import Dispatcher
from aiogram.types import CallbackQuery

from tgbot.handlers.admin_menu.feedback_receive import Feedback
from tgbot.keyboards.feedback_inilne import feedback_inline, feedback_callback
from tgbot.keyboards.main_menu_inline import menu_button_callback, main_menu_keyboard, admin_menu_keyboard
from tgbot.misc.states import User, AdminMenu


async def feedback_menu(call: CallbackQuery):
    await call.answer()
    await call.message.edit_text(f"<b>F.A.Q</b>\n\n"
                                 f"1. Что означает 💰?\n"
                                 f"<b>Один 💰 равен 1 UAH</b>\n"
                                 f"2. --------\n"
                                 f"3. --------\n\n"
                                 f"Не нашел ответа на свой вопрос?\n"
                                 f"Используй функцию <b><i>Написать в поддержку</i></b>",
                                 reply_markup=feedback_inline)


async def cancel_feedback(call: CallbackQuery):
    callback = call.get_current().data
    config = call.bot.get('config')

    if "cancel_feedback" in callback:
        if call.from_user.id in config.tg_bot.admin_ids:
            await call.message.edit_text(f"Главное меню📀\n\n"
                                         f"<i>режим администратора</i>",
                                         reply_markup=admin_menu_keyboard)
            await AdminMenu.adminMenu.set()
        else:
            await call.message.edit_text(f"Главное меню📀\n\n",
                                         reply_markup=main_menu_keyboard)
            await User.mainMenu.set()

            await User.mainMenu.set()
    elif "cancel_receive" in callback:
        await call.message.delete_reply_markup()
        await call.message.answer(f"<b>F.A.Q</b>\n\n"
                                     f"1. Что означает 💰?\n"
                                     f"<b>Один 💰 равен 1 UAH</b>\n"
                                     f"2. --------\n"
                                     f"3. --------\n\n"
                                     f"Не нашел ответа на свой вопрос?\n"
                                     f"Используй функцию <b><i>Написать в поддержку</i></b>",
                                     reply_markup=feedback_inline)


def register_feedback_handler(dp: Dispatcher):
    dp.register_callback_query_handler(feedback_menu, menu_button_callback.filter(button="feedback"),
                                       state=[User.mainMenu, AdminMenu.adminMenu])
    dp.register_callback_query_handler(cancel_feedback, feedback_callback.filter(button=["cancel_feedback",
                                                                                         "cancel_receive"]),
                                       state=[User.mainMenu, AdminMenu.adminMenu, Feedback.getFeedback])
