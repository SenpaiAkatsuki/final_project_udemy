from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData


referral_button_callback = CallbackData("referral", "button")

referral_keyboard = InlineKeyboardMarkup(row_width=1,
                                         inline_keyboard=[
                                             [
                                                 InlineKeyboardButton(text="Показать рефералов🎟",
                                                                      callback_data=referral_button_callback.new(
                                                                          button="show_referrals"
                                                                      ))
                                             ],
                                             [
                                                 InlineKeyboardButton(text="Назад🔚",
                                                                      callback_data="referral:cancel_referrals"
                                                                      )
                                             ]
                                         ])
