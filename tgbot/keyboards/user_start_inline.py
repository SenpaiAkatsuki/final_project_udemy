from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

user_callback = CallbackData("button", "type")

verification_buttons = InlineKeyboardMarkup(row_width=1,
                                            inline_keyboard=[
                                                [
                                                    InlineKeyboardButton(
                                                        text="Проверить подписку на группу☑️",
                                                        callback_data=user_callback.new(
                                                            type="member_check"
                                                        )
                                                    )
                                                ],
                                                [
                                                    InlineKeyboardButton(
                                                        text="Ввести код приглашения🔢",
                                                        callback_data="button:invite_code"
                                                    )
                                                ],
                                            ])

cancel_keyboard = InlineKeyboardMarkup(row_width=1,
                                       inline_keyboard=[
                                           [
                                               InlineKeyboardButton(
                                                   text="Назад🔚",
                                                   callback_data=user_callback.new(
                                                       type="cancel"
                                                   )
                                               )
                                           ]
                                       ]
                                       )
