import asyncio
import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.exceptions import ChatNotFound

from tgbot.integrations.telegraph import FileUploader
from tgbot.keyboards.admin_inline import admin_panel_callback
from tgbot.keyboards.announcement_inline import announcement_inline_keyboard, announcement_callback
from tgbot.keyboards.main_menu_inline import admin_menu_keyboard
from tgbot.misc.states import AdminMenu, Announcement


async def get_announcement_text(call: types.CallbackQuery):
    await call.message.delete_reply_markup()
    await call.message.answer("Напишите пост для всех пользователей📝")

    await Announcement.getAnnouncementText.set()


async def confirm_announcement_text(message: types.Message, state: FSMContext):
    if message.text:
        await state.update_data(
            announcement=message.text
        )
    else:
        await message.answer("Напишите текст для поста📝")
        await Announcement.getAnnouncementText.set()
        return
    await message.answer(f"Ваш <b>пост</b> для пользователей📝:\n"
                         f"{message.text}\n\n"
                         f"Отправить?",
                         reply_markup=announcement_inline_keyboard)

    await Announcement.sendAnnouncement.set()


async def add_photo_announcement(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await call.message.edit_text(f"{data.get('announcement')}")
    await call.message.answer("Пришлите фото для поста📸")

    await Announcement.getAnnouncementPhoto.set()


async def confirm_photo_announcement(message: types.Message, state: FSMContext, file_uploader: FileUploader):
    data = await state.get_data()
    if message.photo:
        uploaded_photo = await file_uploader.upload_photo(message.photo[-1])
        await state.update_data(
            photo_announcement=uploaded_photo.link
        )
    else:
        await message.answer("Пришлите фото для поста📸")
        await Announcement.getAnnouncementPhoto.set()
        return

    await message.answer_photo(photo=message.photo[-1].file_id,
                               caption=f"{data.get('announcement')}")
    await message.answer(f"Отправить пост пользователям?",
                         reply_markup=announcement_inline_keyboard)

    await Announcement.sendAnnouncement.set()


async def accept_announcement(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    config = call.bot.get('config')
    data = await state.get_data()
    db = call.bot.get('db')

    users = await db.select_all_users()
    try:
        if data.get('photo_announcement'):
            for usr in users:
                await call.bot.send_photo(chat_id=usr['telegram_id'],
                                          photo=data.get('photo_announcement'),
                                          caption=data.get('announcement'))
        else:
            for usr in users:
                await call.bot.send_message(usr['telegram_id'],
                                            text=data.get('announcement'))
    except Exception as e:
        logging.error(f"Error while sending announcement: {e}")

    await call.message.edit_text("<b>Рассылка завершена✔️</b>", )
    await call.message.answer(f"<b>Меню администратора📀</b>\n\n",
                              reply_markup=admin_menu_keyboard)
    await AdminMenu.adminMenu.set()


async def cancel_announcement(call: CallbackQuery):
    await call.message.edit_text("Отмена рассылки❌",
                                 reply_markup=admin_menu_keyboard)

    await AdminMenu.adminMenu.set()


def register_announcement_handler(dp: Dispatcher):
    dp.register_callback_query_handler(get_announcement_text,
                                       admin_panel_callback.filter(button="announcement"),
                                       state=AdminMenu.adminMenu)
    dp.register_message_handler(confirm_announcement_text,
                                state=Announcement.getAnnouncementText)

    dp.register_callback_query_handler(add_photo_announcement,
                                       announcement_callback.filter(button="add_photo"),
                                       state=Announcement.sendAnnouncement),
    dp.register_message_handler(confirm_photo_announcement,
                                state=Announcement.getAnnouncementPhoto,
                                content_types=types.ContentTypes.ANY)

    dp.register_callback_query_handler(accept_announcement,
                                       announcement_callback.filter(button="confirm_announcement"),
                                       state=[Announcement.sendAnnouncement])
    dp.register_callback_query_handler(cancel_announcement,
                                       announcement_callback.filter(button="cancel_announcement"),
                                       state=Announcement.sendAnnouncement)
