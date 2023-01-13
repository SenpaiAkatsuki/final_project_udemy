from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, inline_keyboard
from aiogram.utils.callback_data import CallbackData

admin_panel_callback = CallbackData("admin", "button")
cancel_callback = CallbackData("cancel", "button")

admin_panel_buttons = InlineKeyboardMarkup(row_width=2,
                                           inline_keyboard=[
                                               [
                                                   InlineKeyboardButton(text="Добавить товар➕",
                                                                        callback_data="admin:add_product")
                                               ],
                                               [
                                                   InlineKeyboardButton(text="Рассылка📢",
                                                                        callback_data="admin:announcement"),

                                                   InlineKeyboardButton(text="Ответ на жалобы💬",
                                                                        callback_data="admin:feedback_answer")
                                               ],
                                               [
                                                   InlineKeyboardButton(text="Режим пользователя🪄",
                                                                        callback_data="admin:return_to_user")
                                               ]
                                           ])

product_creation_cancel = InlineKeyboardMarkup(row_width=1,
                                               inline_keyboard=[
                                                   [
                                                       InlineKeyboardButton(text="Отменить🔚",
                                                                            callback_data=cancel_callback.new(
                                                                                button="cancel_action"
                                                                            ))
                                                   ]
                                               ])
