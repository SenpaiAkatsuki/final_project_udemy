from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

feedback_callback = CallbackData("feedback", "button")

feedback_inline = InlineKeyboardMarkup(row_width=1,
                                       inline_keyboard=[
                                           [
                                               InlineKeyboardButton("Написать в поддержку📲",
                                                                    callback_data=feedback_callback.new(
                                                                        button="call_support"
                                                                    ))
                                           ],
                                           [
                                               InlineKeyboardButton(text="Назад🔚",
                                                                    callback_data="feedback:cancel_feedback"
                                                                    )
                                           ]
                                       ])

confirm_feedback_inline = InlineKeyboardMarkup(row_width=2,
                                               inline_keyboard=[
                                                   [
                                                       InlineKeyboardButton("Отправить☑️",
                                                                            callback_data=feedback_callback.new(
                                                                                button="send_feedback"
                                                                            )),

                                                       InlineKeyboardButton("Отменить❌",
                                                                            callback_data="feedback:cancel_receive")
                                                   ]
                                               ])

answer_feedback_inline = InlineKeyboardMarkup(row_width=2,
                                              inline_keyboard=[
                                                  [
                                                      InlineKeyboardButton("Ответить на заявку☑️",
                                                                           callback_data="feedback:answer_feedback")
                                                  ],
                                                  [
                                                      InlineKeyboardButton("Отклонить заявку❌",
                                                                           callback_data="feedback:decline_feedback")
                                                  ]
                                              ])

get_next_feedback_inline = InlineKeyboardMarkup(row_width=1,
                                                inline_keyboard=[
                                                    [
                                                        InlineKeyboardButton("Следующая заявка➡️",
                                                                             callback_data="feedback:get_next_feedback")
                                                    ],
                                                    [
                                                        InlineKeyboardButton("Назад в меню🔚",
                                                                             callback_data="feedback:cancel_feedback")
                                                    ]
                                                ])
