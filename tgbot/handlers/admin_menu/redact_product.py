import re

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from tgbot.integrations.telegraph import FileUploader
from tgbot.keyboards.purchase_inline import redact_product_inline, redact_callback, payment_inline_admin
from tgbot.misc.states import Purchase, RedactProduct, User


async def redact_menu(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await call.message.delete_reply_markup()
    await call.message.answer("Выберете изменения⚙️",
                              reply_markup=redact_product_inline)

    await state.update_data(
        product_to_redact=data.get('product_id')
    )
    await RedactProduct.changeRedaction.set()


async def cancel_redact(call: types.CallbackQuery, state: FSMContext):
    db = call.bot.get('db')
    data = await state.get_data()
    selected = await db.select_product(product_id=data['product_to_redact'])

    # await call.bot.delete_message(chat_id=call.from_user.id,
    #                               message_id=call.message.message_id - 1)

    await call.message.delete_reply_markup()
    await call.message.answer_photo(photo=selected.get('photo'),
                                    caption=f"Товар: <b>{selected.get('name')}</b>\n\n"
                                            f"{selected.get('description')}\n\n"
                                            f"Количество товара: {selected.get('quantity')}\n"
                                            f"Цена: {selected.get('price')}",
                                    reply_markup=payment_inline_admin)

    await Purchase.selectedProduct.set()


async def change_product(call: types.CallbackQuery, state: FSMContext):
    callback = call.get_current().data

    if "change_name" in callback:
        await call.message.answer("Введите новое название товара📝")
        await state.update_data(
            redact_value="name"
        )

    elif "change_description" in callback:
        await call.message.answer("Введите новое описание товара📝")
        await state.update_data(
            redact_value="description"
        )

    elif "change_price" in callback:
        await call.message.answer("Введите новую цену товара📝")
        await state.update_data(
            redact_value="price"
        )

    elif "change_photo" in callback:
        await call.message.answer("Отправьте новое фото товара📝")
        await state.update_data(
            redact_value="photo"
        )

    await call.message.delete_reply_markup()
    await RedactProduct.changeValue.set()


async def change_product_value(message: types.Message, state: FSMContext, file_uploader: FileUploader):
    data = await state.get_data()
    db = message.bot.get('db')
    value_to_redact = data.get('redact_value')
    product = await db.select_product(product_id=data.get('product_to_redact'))

    if "name" in value_to_redact:
        await db.update_product_name(message.text,
                                     product.get('product_id'))

    elif "description" in value_to_redact:
        await db.update_product_description(message.text,
                                            product.get('product_id'))

    elif "price" in value_to_redact:
        if re.compile(r'^\d{1,10}$').match(message.text):  # 1 - 10 digits
            await db.update_product_price(int(message.text),
                                          product.get('product_id'))
        else:
            await message.answer("Некорректная цена, попробуйте еще раз")
            await RedactProduct.changeValue.set()
            return

    elif "photo" in value_to_redact:
        if message.photo:
            uploaded_photo = await file_uploader.upload_photo(message.photo[-1])
            await db.update_product_photo(uploaded_photo.link,
                                          product.get('product_id'))
        else:
            await message.answer("Неверный формат❌\n\n"
                                 "Пришлите фото товара в формате <b>jpg</b> или <b>png</b>")
            await RedactProduct.changeValue.set()
            return

    await message.answer("Товар изменен☑️\n\n"
                         "<i>для вызова меню используйте:</i> /start")

    await User.mainMenu.set()


def redact_product_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(redact_menu, redact_callback.filter(button="redact_product"),
                                       state=Purchase.selectedProduct)

    dp.register_callback_query_handler(change_product, redact_callback.filter(button=["change_name",
                                                                                      "change_description",
                                                                                      "change_price",
                                                                                      "change_photo"]),
                                       state=RedactProduct.changeRedaction)

    dp.register_message_handler(change_product_value, state=RedactProduct.changeValue,
                                content_types=types.ContentTypes.ANY)

    dp.register_callback_query_handler(cancel_redact, redact_callback.filter(button="cancel"),
                                       state=RedactProduct.changeRedaction)
