from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

purchase_callback = CallbackData("buy", "button")

redact_callback = CallbackData("redact", 'button')


def purchase_keyboard(key, bot):
    show_purchase_keyboard = InlineKeyboardMarkup(row_width=2,
                                                  inline_keyboard=[
                                                      [
                                                          InlineKeyboardButton("Показать товар📚",
                                                                               url=f"https://t.me/{bot}?start={key}")
                                                      ]
                                                  ])
    return show_purchase_keyboard


payment_inline = InlineKeyboardMarkup(row_width=1,
                                      inline_keyboard=[
                                          [
                                              InlineKeyboardButton("Купить товар💰",
                                                                   callback_data="buy:buy_product")
                                          ]
                                      ])

payment_inline_admin = InlineKeyboardMarkup(row_width=1,
                                            inline_keyboard=[

                                            ])
payment_inline_admin.inline_keyboard.append(payment_inline.inline_keyboard[0])
payment_inline_admin.inline_keyboard.append([
    InlineKeyboardButton("Редактировать🔧",
                         callback_data=redact_callback.new(
                             button="redact_product"
                         ))
])

redact_product_inline = InlineKeyboardMarkup(row_width=1,
                                             inline_keyboard=[
                                                 [
                                                     InlineKeyboardButton("Имя💬",
                                                                          callback_data=redact_callback.new(
                                                                              button="change_name"
                                                                          )),
                                                     InlineKeyboardButton("Описание📝",
                                                                          callback_data="redact:change_description")
                                                 ],
                                                 [
                                                     InlineKeyboardButton("Цена💰",
                                                                          callback_data="redact:change_price"
                                                                          ),
                                                     InlineKeyboardButton("Фото📷",
                                                                          callback_data="redact:change_photo"
                                                                          ),
                                                 ],
                                                 [
                                                     InlineKeyboardButton("Отмена❌",
                                                                          callback_data="redact:cancel"
                                                                          )
                                                 ]
                                             ])

buy_inline = InlineKeyboardMarkup(row_width=2,
                                  inline_keyboard=[
                                      [
                                          InlineKeyboardButton("За баланс💵",
                                                               callback_data=purchase_callback.new(
                                                                   button="purchase_by_balance"
                                                               )),
                                          InlineKeyboardButton("Через monobank💳",
                                                               callback_data="buy:purchase_by_mono")
                                      ],
                                      [
                                          InlineKeyboardButton("Отмена❌",
                                                               callback_data="buy:cancel")
                                      ]
                                  ])

check_payment_mono = InlineKeyboardMarkup(row_width=1,
                                          inline_keyboard=[
                                              [
                                                  InlineKeyboardButton("Проверить оплату💵",
                                                                       callback_data=purchase_callback.new(
                                                                           button="check_payment_mono"
                                                                       ))
                                              ],
                                              [
                                                  InlineKeyboardButton("Отмена❌",
                                                                       callback_data="buy:cancel")
                                              ]
                                          ])

cancel_purchase_inline = InlineKeyboardMarkup(row_width=1,
                                              inline_keyboard=[
                                                  [
                                                      InlineKeyboardButton("Отмена❌",
                                                                           callback_data="buy:cancel")
                                                  ]
                                              ])
