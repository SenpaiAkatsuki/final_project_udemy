from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

menu_button_callback = CallbackData("menu", "button")

cancel_callback = CallbackData("cancel", "button")

main_menu_keyboard = InlineKeyboardMarkup(row_width=2,
                                          inline_keyboard=[
                                              [
                                                  InlineKeyboardButton(text="Каталог📕",
                                                                       switch_inline_query_current_chat=""
                                                                       )
                                              ],
                                              [
                                                  InlineKeyboardButton(text="Обратная связь💬",
                                                                       callback_data="menu:feedback"),
                                                  InlineKeyboardButton(text="Реферал®️",
                                                                       callback_data="menu:referral")
                                              ]
                                          ])

cancel_to_menu = InlineKeyboardMarkup(row_width=1,
                                      inline_keyboard=[
                                          [
                                              InlineKeyboardButton(text="Назад🔚",
                                                                   callback_data=cancel_callback.new(
                                                                       button="cancel"
                                                                   ))
                                          ]
                                      ])
