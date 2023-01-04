from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from tgbot.keyboards.main_menu_inline import main_menu_keyboard, admin_menu_keyboard
from tgbot.keyboards.purchase_inline import payment_inline, buy_inline, purchase_callback, cancel_purchase_inline, \
    payment_inline_admin
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
                                                   f"Количество товара: {selected.get('quantity')}\n"
                                                   f"Цена: {selected.get('price')}",
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
        await call.message.answer(
            f"На вашем балансе бота: {user['balance']}💰\n\n"
            f"<b>Выберите способ оплаты</b>",
            reply_markup=buy_inline)


async def pick_quantity_balance(call: CallbackQuery):
    await call.message.delete_reply_markup()
    await call.message.answer("Введите количество товара для покупки📝",
                              reply_markup=cancel_purchase_inline)

    await Purchase.selectQuantity.set()


async def buy_balance(message: types.Message, state: FSMContext):
    data = await state.get_data()
    db = message.bot.get('db')
    try:
        quantity = int(message.text)
    except ValueError:
        await message.bot.edit_message_reply_markup(chat_id=message.chat.id,
                                                    message_id=message.message_id - 1)
        await message.answer("Введите число📝",
                             reply_markup=cancel_purchase_inline)
        await Purchase.selectQuantity.set()
        return

    user = await db.select_user(telegram_id=message.from_user.id)
    product = await db.select_product(product_id=data.get('product_id'))
    if quantity <= product['quantity']:
        if user['balance'] >= product['price'] * quantity:

            await db.change_quantity(quantity=product['quantity'] - quantity, product_id=product['product_id'])
            await db.change_user_balance(balance=user['balance'] - product['price'], telegram_id=message.from_user.id)
            await message.answer(f"Успешная покупка!\n\n"
                                 f"С вашего баланса снято {product['price']} остаток баланса "
                                 f"{user['balance'] - product['price']}\n\n"
                                 f"<i>для вызова меню используйте:</i> /start")

            await User.mainMenu.set()

        elif user['balance'] < product['price'] * quantity:
            await message.answer(
                f"На вашем балансе бота: {user['balance']}💰\n\n"
                f"<b>❗️Недостаточно средств на балансе❗️</b>",
                reply_markup=buy_inline)

            await Purchase.selectedProduct.set()

        else:
            await message.answer("../error")

            await User.mainMenu.set()
    elif product['quantity'] == 0:
        await message.bot.edit_message_reply_markup(chat_id=message.chat.id,
                                                    message_id=message.message_id - 1)
        await message.answer("Товар закончился❌",
                             reply_markup=cancel_purchase_inline)

        await Purchase.selectQuantity.set()
    else:
        await message.delete_reply_markup()
        await message.bot.edit_message_reply_markup(chat_id=message.chat.id,
                                                    message_id=message.message_id - 1)
        await message.answer("Неверное количество товара❌\n\n"
                             "Укажите количество товара для покупки📝",
                             reply_markup=cancel_purchase_inline)

        await Purchase.selectQuantity.set()


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
                                              PurchaseMono.monoComplete])
    dp.register_message_handler(deeplink_purchase,
                                commands="start",
                                state=[User.mainMenu, AdminMenu.adminMenu]),
    dp.register_callback_query_handler(purchase_product,
                                       purchase_callback.filter(button="buy_product"),
                                       state=Purchase.selectedProduct)
    dp.register_callback_query_handler(pick_quantity_balance,
                                       purchase_callback.filter(button='purchase_by_balance'),
                                       state=Purchase.selectedProduct)
    dp.register_message_handler(buy_balance,
                                state=Purchase.selectQuantity)
