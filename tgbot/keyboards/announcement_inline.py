from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

announcement_callback = CallbackData("announcement", "button")


announcement_inline_keyboard = InlineKeyboardMarkup(row_width=2,
                                                    inline_keyboard=[
                                                        [
                                                            InlineKeyboardButton(text="Подтвердить☑️",
                                                                                 callback_data=announcement_callback.new(
                                                                                    button="confirm_announcement"
                                                                                 )),
                                                            InlineKeyboardButton(text="Отменить❌",
                                                                                 callback_data=
                                                                                 "announcement:cancel_announcement")
                                                        ],
                                                        [
                                                            InlineKeyboardButton(text="Редактировать⚙️",
                                                                                 callback_data=
                                                                                 "announcement:redact_announcement")
                                                        ]
                                                    ])