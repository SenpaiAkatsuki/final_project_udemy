import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import CallbackQuery
from aiogram.utils.exceptions import ChatNotFound

from tgbot.keyboards.admin_inline import admin_panel_callback
from tgbot.keyboards.announcement_inline import announcement_inline_keyboard, announcement_callback
from tgbot.keyboards.main_menu_inline import admin_menu_keyboard
from tgbot.misc.states import AdminMenu


class Announcement(StatesGroup):
    getAnnouncement = State()
    redactAnnouncement = State()


async def get_announcement(call: types.CallbackQuery):
    await call.answer()
    await call.message.delete_reply_markup()
    await call.message.answer("Напишите пост для всех пользователей📝")

    await Announcement.getAnnouncement.set()


async def confirm_announcement(message: types.Message, state: FSMContext):
    await message.answer(f"Ваш пост для пользователей✉️:\n\n"
                         f"{message.text}\n\n"
                         f"Отправить?",
                         reply_markup=announcement_inline_keyboard)

    await state.update_data(
        announcement=message.text,
    )


async def accept_announcement(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    config = call.bot.get('config')
    data = await state.get_data()
    db = call.bot.get('db')

    users = await db.select_all_users()

    for usr in users:
        if usr['telegram_id'] not in config.tg_bot.admin_ids:
            try:
                await call.bot.send_message(usr['telegram_id'],
                                            text=data.get('announcement'))
            except ChatNotFound:
                logging.info(f"no such user found")

    await call.message.edit_text(f"<b>Ваш пост отправлен пользователям</b>✔️\n\n"
                                 f"{data.get('announcement')}",
                                 reply_markup=admin_menu_keyboard)
    await AdminMenu.adminMenu.set()


async def redact_announcement(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    await call.message.edit_text(f"Ваш пост:\n\n"
                                 f"{data.get('announcement')}",
                                 reply_markup=None)
    await call.message.answer("Напишите новую версию поста📝")

    await Announcement.getAnnouncement.set()


async def cancel_announcement(call: CallbackQuery):
    await call.message.edit_text("Отмена рассылки❌",
                                 reply_markup=admin_menu_keyboard)

    await AdminMenu.adminMenu.set()


def register_announcement_handler(dp: Dispatcher):
    dp.register_callback_query_handler(get_announcement,
                                       admin_panel_callback.filter(button="announcement"),
                                       state=AdminMenu.adminMenu)
    dp.register_message_handler(confirm_announcement,
                                state=Announcement.getAnnouncement)
    dp.register_callback_query_handler(accept_announcement,
                                       announcement_callback.filter(button="confirm_announcement"),
                                       state=Announcement.getAnnouncement)
    dp.register_callback_query_handler(cancel_announcement,
                                       announcement_callback.filter(button="cancel_announcement"),
                                       state=Announcement.getAnnouncement)
    dp.register_callback_query_handler(redact_announcement,
                                       announcement_callback.filter(button="redact_announcement"),
                                       state=Announcement.getAnnouncement)
