# import datetime
# import logging
#
# import monobank
# from aiogram import types, Dispatcher
# from aiogram.dispatcher import FSMContext
# from aiogram.types import CallbackQuery
# from aiogram.utils.exceptions import MessageCantBeEdited
# from monobank import TooManyRequests
#
# from tgbot.handlers.main_menu.purchase_handler import Purchase
# from tgbot.keyboards.main_menu_inline import main_menu_keyboard, admin_menu_keyboard
# from tgbot.keyboards.purchase_inline import check_payment_mono, purchase_callback, cancel_purchase_inline
# from tgbot.misc.states import PurchaseMono, User
#
#
# async def select_quantity_mono(call: types.CallbackQuery, state: FSMContext):
#     data = await state.get_data()
#     db = call.bot.get('db')
#     product = await db.select_product(product_id=data.get('product_id'))
#
#     if product['quantity'] == 0:
#         await call.answer(text="Товар закончился🤷‍♂️", show_alert=True)
#
#     await Purchase.selectedProduct.set()
#
#     await call.message.delete_reply_markup()
#     await call.message.answer(f"Введите количество товара для покупки📝",
#                               reply_markup=cancel_purchase_inline)
#
#     await PurchaseMono.checkPayment.set()
#
#
# async def purchase_buy_mono(message: types.Message, state: FSMContext):
#     data = await state.get_data()
#     db = message.bot.get('db')
#
#     try:
#         if message.text:
#             quantity = int(message.text)
#         else:
#             await message.bot.edit_message_reply_markup(chat_id=message.chat.id,
#                                                         message_id=message.message_id - 1)
#             await message.answer("Неверное количество товара❌\n\n"
#                                  "Укажите количество товара для покупки📝",
#                                  reply_markup=cancel_purchase_inline)
#
#             await PurchaseMono.checkPayment.set()
#             return
#
#         await state.update_data(
#             user_quantity=quantity
#         )
#
#         product = await db.select_product(product_id=data.get('product_id'))
#         price = product['price'] * quantity
#         quantity = int(message.text)
#         link = "https://send.monobank.ua/Cu1UerRfu?f=enable&amount={amount}&text={text}"
#         if product['quantity'] >= quantity:
#             await message.bot.edit_message_reply_markup(chat_id=message.chat.id,
#                                                         message_id=message.message_id - 1, )
#             await message.answer(text=link.format(amount=f"{price}", text=f"{message.from_user.id}"))
#             await message.answer(text=f"Оплатите сумму в размере {price}₴,\n"
#                                       f"после нажмите на кнопку для проверки оплаты💵\n\n"
#                                       f"Обратите внимание на то, что оплата с браузера поддерживает платежи от 100₴❗️\n"
#                                       f"Если ваша сумма оплаты выше 100₴, то проведите оплату через мобильное приложение❗️",
#                                  reply_markup=check_payment_mono)
#
#             await PurchaseMono.monoComplete.set()
#
#         elif quantity == 0:
#             await message.bot.edit_message_reply_markup(chat_id=message.chat.id,
#                                                         message_id=message.message_id - 1, )
#             await message.answer(text="Количество товара не может быть равно 0🤔",
#                                  reply_markup=cancel_purchase_inline)
#         else:
#             await message.bot.edit_message_reply_markup(chat_id=message.chat.id,
#                                                         message_id=message.message_id - 1, )
#             await message.answer("Неверное количество товара❌\n\n"
#                                  "Укажите количество товара для покупки📝",
#                                  reply_markup=cancel_purchase_inline)
#
#             await PurchaseMono.checkPayment.set()
#     except ValueError:
#         await message.bot.edit_message_reply_markup(chat_id=message.chat.id,
#                                                     message_id=message.message_id - 1)
#         await message.answer("Неверное количество товара❌\n\n"
#                              "Укажите количество товара для покупки📝",
#                              reply_markup=cancel_purchase_inline)
#
#         await PurchaseMono.checkPayment.set()
#
#
# async def check_payment(call: CallbackQuery, state: FSMContext):
#     await call.answer(cache_time=1)
#     data = await state.get_data()
#     config = call.bot.get('config')
#     db = call.bot.get('db')
#     logging.info('working')
#
#     mono = monobank.Client(config.misc.mono_token)
#     product = await db.select_product(product_id=data.get('product_id'))
#     user = await db.select_user(telegram_id=call.from_user.id)
#
#     try:
#         monoData = mono.get_statements(f'{config.misc.mono_card_id}',
#                                        datetime.datetime.now() - datetime.timedelta(days=2),
#                                        datetime.datetime.now())
#         print(monoData)
#         if monoData:
#             for k in monoData:
#                 if k['id'] not in user['purchase_list']:
#                     if str(call.from_user.id) in k.values() and str(product['price']) + "00" == str(k['amount']):
#                         await call.message.delete_reply_markup()
#                         await call.message.answer_photo(photo=product['photo'],
#                                                         caption=f"Оплата☑️\n\n"
#                                                                 f"Товар: <b>{product['name']}</b>\n"
#                                                                 f"{product['description']}\n\n"
#                                                                 f"Количество: {data.get('user_quantity')}\n"
#                                                                 f"Номер заказа: <code>{k['id']}</code>")
#
#                         await db.insert_purchase_list(purchase_id=k['id'],
#                                                       telegram_id=call.from_user.id)
#                         await db.change_quantity(quantity=product['quantity'] - int(data['user_quantity']),
#                                                  product_id=product['product_id'])
#
#                         if call.from_user.id in config.tg_bot.admin_ids:
#                             await call.message.answer("Admin Menu",
#                                                       reply_markup=admin_menu_keyboard)
#
#                             await User.mainMenu.set()
#                         else:
#                             await call.message.answer("Main Menu",
#                                                       reply_markup=main_menu_keyboard)
#
#                             await User.mainMenu.set()
#
#                         break
#             else:
#                 await call.message.answer(f"Оплата не найдена, попробуйте еще раз❕\n\n"
#                                           f"Убедитесь что вы оставили комментарий при оплате❔\n"
#                                           f"Если есть вопросы используйте вкладку <b>помощь</b>\n"
#                                           f"<i>Главное меню -> Обратная связь</i>")
#
#                 await PurchaseMono.monoComplete.set()
#         else:
#             print('working here')
#             await call.message.answer("Платеж не найден❔ "
#                                       "Возможно стоит подождать, иногда это занимает пару минут")
#
#             await PurchaseMono.monoComplete.set()
#
#     except TooManyRequests:
#         await call.message.answer("Слишком много запросов")
#
#
# def register_mono_handler(dp: Dispatcher):
#     # dp.register_callback_query_handler(select_quantity_mono,
#     #                                    purchase_callback.filter(button='purchase_by_mono'),
#     #                                    state=[Purchase.selectedProduct])
#     dp.register_message_handler(purchase_buy_mono,
#                                 state=PurchaseMono.checkPayment,
#                                 content_types=types.ContentType.ANY)
#     dp.register_callback_query_handler(check_payment,
#                                        purchase_callback.filter(button="check_payment_mono"),
#                                        state=[PurchaseMono.monoComplete])
