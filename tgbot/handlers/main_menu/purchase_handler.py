import datetime
import re

import monobank
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from monobank import TooManyRequests

from tgbot.keyboards.main_menu_inline import main_menu_keyboard, admin_menu_keyboard
from tgbot.keyboards.purchase_inline import payment_inline, buy_inline, purchase_callback, cancel_purchase_inline, \
    payment_inline_admin, check_payment_inline
from tgbot.misc.rate_limit import rate_limit
from tgbot.misc.states import AdminMenu, User, Purchase, PurchaseMono


@rate_limit(limit=3)
async def deeplink_purchase(message: types.Message, state: FSMContext):
    config = message.bot.get('config')
    db = message.bot.get('db')

    product_ids = await db.get_products()
    arguments = message.get_args()
    keyboard = payment_inline

    if arguments:
        for product in product_ids:
            if arguments in product[0]:
                if message.from_user.id in config.tg_bot.admin_ids:
                    keyboard = payment_inline_admin
                selected = await db.select_product(product_id=product[0])
                await message.answer_photo(photo=selected.get('photo'),
                                           caption=f"Товар: <b>{selected.get('name')}</b>\n\n"
                                                   f"{selected.get('description')}\n\n"
                                                   f"Количество товара: <b>{selected.get('quantity')}</b>\n"
                                                   f"Цена: <b>{selected.get('price')}</b>💰",
                                           reply_markup=keyboard)

                await Purchase.selectedProduct.set()

                await state.update_data(
                    product_id=selected.get('product_id'),
                    quantity=selected.get('quantity')
                )
                break
            elif arguments == str(message.from_user.id):
                await message.answer("Нельзя пригласить себя💔")
                break
            else:
                pass
    else:
        if message.from_user.id in config.tg_bot.admin_ids:
            await message.answer("Добро пожаловать <b>Админ</b>📀",
                                 reply_markup=admin_menu_keyboard)

            await User.mainMenu.set()
        else:
            await message.answer("<b>Меню пользователя📀</b>",
                                 reply_markup=main_menu_keyboard)

            await User.mainMenu.set()


async def purchase_product(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=1)
    db = call.bot.get('db')
    data = await state.get_data()

    user = await db.select_user(telegram_id=call.from_user.id)
    product = await db.select_product(product_id=data.get('product_id'))

    if product['quantity'] == 0:
        await call.message.answer(text=f"Товар закончился🤷‍♂️\n\n"
                                       f"<i>Для вызова меню используйте:</i> /start")

    else:
        await call.message.delete_reply_markup()
        await call.message.answer(
            f"На вашем балансе бота: {user['balance']}💰\n\n"
            f"<b>Выберите способ оплаты</b>",
            reply_markup=buy_inline)


async def pick_quantity_balance(call: CallbackQuery, state: FSMContext):
    query = call.get_current().data
    await state.update_data(
        purchase_query=query
    )

    await call.message.delete_reply_markup()
    await call.message.answer("Введите количество товара для покупки📝",
                              reply_markup=cancel_purchase_inline)

    await Purchase.selectQuantity.set()


async def get_shipping_address(message: types.Message, state: FSMContext):
    try:
        quantity = int(message.text)
        await state.update_data(
            user_quantity=quantity
        )

        await message.bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=message.message_id - 1,
                                            text=f"Количество товара для покупки☑️", )
        await message.answer("Введите адрес доставки📝",
                             reply_markup=cancel_purchase_inline)

        await Purchase.selectAddress.set()

    except (ValueError, TypeError):
        await message.bot.edit_message_reply_markup(chat_id=message.chat.id,
                                                    message_id=message.message_id - 1)
        await message.answer("Неверное количество товара❌\n\n"
                             "Введите <b>число</b> товара для покупки📝",
                             reply_markup=cancel_purchase_inline)
        await Purchase.selectQuantity.set()
        return


async def purchase_payment(message: types.Message, state: FSMContext):
    data = await state.get_data()
    db = message.bot.get('db')
    pattern = re.compile(r'^.{1,255}$')  # 255 characters max

    user = await db.select_user(telegram_id=message.from_user.id)
    product = await db.select_product(product_id=data.get('product_id'))
    user_quantity = data.get('user_quantity')
    total_price = product['price'] * user_quantity

    if message.text and pattern.match(message.text):
        user_address = message.text
        await state.update_data(
            user_address=user_address
        )
        if "purchase_by_balance" in data.get('purchase_query'):
            if user_quantity <= product['quantity']:
                if user['balance'] >= total_price:

                    await db.change_quantity(quantity=product['quantity'] - user_quantity,
                                             product_id=product['product_id'])
                    await db.change_user_balance(balance=user['balance'] - total_price,
                                                 telegram_id=message.from_user.id)
                    await message.answer_photo(photo=product['photo'],
                                               caption=f"Оплата☑️\n\n"
                                                       f"Товар: <b>{product['name']}</b>\n"
                                                       f"{product['description']}\n\n"
                                                       f"Количество: {data.get('user_quantity')}\n"
                                                       f"Адрес доставки: {user_address}\n")

                    await User.mainMenu.set()

                elif user['balance'] < product['price'] * user_quantity:
                    await message.answer(
                        f"На вашем балансе бота: {user['balance']}💰\n\n"
                        f"<b>❗️Недостаточно средств на балансе❗️</b>",
                        reply_markup=buy_inline)

                    await Purchase.selectedProduct.set()
            else:
                await message.bot.edit_message_reply_markup(chat_id=message.chat.id,
                                                            message_id=message.message_id - 1)
                await message.answer("Неверное количество товара❌\n\n"
                                     "Введите <b>число</b> товара для покупки📝",
                                     reply_markup=cancel_purchase_inline)
                await User.mainMenu.set()
        else:
            link = "https://send.monobank.ua/Cu1UerRfu?f=enable&amount={amount}&text={text}"
            if user_quantity <= product['quantity']:
                await message.bot.edit_message_reply_markup(chat_id=message.chat.id,
                                                            message_id=message.message_id - 1, )
                await message.answer(text=link.format(amount=f"{total_price}", text=f"{message.from_user.id}"))
                await message.answer(text=f"Оплатите сумму в размере {total_price}₴,\n"
                                          f"после нажмите на кнопку для проверки оплаты💵\n\n"
                                          f"Обратите внимание на то, что оплата с браузера"
                                          f" поддерживает платежи от 100₴❗️\n"
                                          f"Если ваша сумма оплаты выше 100₴,"
                                          f" то проведите оплату через мобильное приложение❗️",
                                     reply_markup=check_payment_inline)

                await PurchaseMono.monoComplete.set()

            else:
                await message.bot.edit_message_reply_markup(chat_id=message.chat.id,
                                                            message_id=message.message_id - 1)
                await message.answer("Неверное количество товара❌\n\n"
                                     "Введите <b>число</b> товара для покупки📝",
                                     reply_markup=cancel_purchase_inline)

                await Purchase.selectQuantity.set()

    else:
        await message.bot.edit_message_reply_markup(chat_id=message.chat.id,
                                                    message_id=message.message_id - 1)
        await message.answer("Неверный формат адреса доставки❌\n\n"
                             "Введите адрес доставки📝",
                             reply_markup=cancel_purchase_inline)
        await Purchase.selectAddress.set()
        return


async def check_payment_mono(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    db = call.bot.get('db')
    config = call.bot.get('config')

    user = await db.select_user(telegram_id=call.from_user.id)
    product = await db.select_product(product_id=data.get('product_id'))
    mono = monobank.Client(config.misc.mono_token)

    try:
        await call.answer(cache_time=5)
        monoData = mono.get_statements(f'{config.misc.mono_card_id}',
                                       datetime.datetime.now() - datetime.timedelta(days=2),
                                       datetime.datetime.now())
        if monoData:
            for k in monoData:
                if k['id'] not in user['purchase_list']:
                    if str(call.from_user.id) in k.values() and str(product['price']) + "00" == str(
                            k['amount']):
                        await call.message.delete_reply_markup()
                        await call.message.answer_photo(photo=product['photo'],
                                                        caption=f"Оплата☑️\n\n"
                                                                f"Товар: <b>{product['name']}</b>\n"
                                                                f"{product['description']}\n\n"
                                                                f"Количество: {data.get('user_quantity')}\n"
                                                                f"Адрес доставки: {data.get('user_address')}\n\n"
                                                                f"Номер заказа: <code>{k['id']}</code>")

                        await db.insert_purchase_list(purchase_id=k['id'],
                                                      telegram_id=call.from_user.id)
                        await db.change_quantity(quantity=product['quantity'] - int(data['user_quantity']),
                                                 product_id=product['product_id'])
                        break
            else:
                await call.message.answer(f"Оплата не найдена, попробуйте еще раз❕\n\n"
                                          f"Убедитесь что вы оставили комментарий при оплате❔\n"
                                          f"Если есть вопросы используйте вкладку <b>помощь</b>\n"
                                          f"<i>Главное меню -> Обратная связь</i>")

                await PurchaseMono.monoComplete.set()
        else:
            await call.message.answer("Платеж не найден❔ "
                                      "Возможно стоит подождать, иногда это занимает пару минут")

            await PurchaseMono.monoComplete.set()

    except TooManyRequests:
        await call.message.answer("Слишком много запросов, пожалуйста подождите❕")


async def cancel_purchase(call: CallbackQuery):
    await call.message.edit_text("Операция отменена❌\n\n"
                                 "<i>для вызова меню используйте:</i> /start",
                                 reply_markup=None)
    await User.mainMenu.set()


def purchase_handler(dp: Dispatcher):
    dp.register_callback_query_handler(cancel_purchase,
                                       purchase_callback.filter(button='cancel'),
                                       state=[Purchase.selectedProduct,
                                              Purchase.selectQuantity,
                                              PurchaseMono.checkPayment,
                                              PurchaseMono.monoComplete,
                                              Purchase.selectAddress])
    dp.register_message_handler(deeplink_purchase,
                                commands="start",
                                state=[User.mainMenu, AdminMenu.adminMenu]),
    dp.register_callback_query_handler(purchase_product,
                                       purchase_callback.filter(button="buy_product"),
                                       state=Purchase.selectedProduct)
    dp.register_callback_query_handler(pick_quantity_balance,
                                       purchase_callback.filter(button=['purchase_by_balance', 'purchase_by_mono']),
                                       state=Purchase.selectedProduct)
    dp.register_message_handler(get_shipping_address,
                                state=Purchase.selectQuantity,
                                content_types=types.ContentTypes.ANY)
    dp.register_message_handler(purchase_payment,
                                state=Purchase.selectAddress,
                                content_types=types.ContentTypes.ANY)
    dp.register_callback_query_handler(check_payment_mono,
                                       purchase_callback.filter(button="check_payment_mono"),
                                       state=[PurchaseMono.monoComplete])
