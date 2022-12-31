from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, inline_keyboard
from aiogram.utils.callback_data import CallbackData

from tgbot.keyboards.main_menu_inline import menu_button_callback

admin_panel_callback = CallbackData("admin", "button")
cancel_callback = CallbackData("cancel", "button")

admin_main_menu = InlineKeyboardMarkup(row_width=2,
                                       inline_keyboard=[
                                           [
                                               InlineKeyboardButton(text="Каталог📕",
                                                                    switch_inline_query_current_chat=""
                                                                    )
                                           ],
                                           [
                                               InlineKeyboardButton(text="Обратная связь🔍",
                                                                    callback_data=menu_button_callback.new(
                                                                        button="feedback"
                                                                    )),
                                               InlineKeyboardButton(text="Рефералы®️",
                                                                    callback_data="menu:referral")
                                           ],
                                           [
                                               InlineKeyboardButton(text="Администрирование🪄",
                                                                    callback_data=admin_panel_callback.new(
                                                                        button="admin_panel"
                                                                    ))
                                           ]
                                       ])

admin_panel_buttons = InlineKeyboardMarkup(row_width=2,
                                           inline_keyboard=[
                                               [
                                                   InlineKeyboardButton(text="Добавить товар➕",
                                                                        callback_data="admin:add_product")
                                               ],
                                               [
                                                   InlineKeyboardButton(text="Рассылка📢",
                                                                        callback_data="admin:announcement"),

                                                   InlineKeyboardButton(text="Просмотреть товары📕",
                                                                        switch_inline_query_current_chat="")
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
