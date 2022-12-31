from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from tgbot.integrations.telegraph import FileUploader
from tgbot.keyboards.admin_inline import admin_panel_buttons
from tgbot.keyboards.purchase_inline import redact_product_inline, redact_callback
from tgbot.misc.db_api.postgres_db import Database
from tgbot.misc.states import Purchase, RedactProduct, AdminMenu


async def redact_menu(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await call.message.delete_reply_markup()
    await call.message.answer("Выберете изменения⚙️",
                              reply_markup=redact_product_inline)

    await state.update_data(
        product_to_redact=data.get('product_id')
    )
    await RedactProduct.changeRedaction.set()


async def cancel_redact(call: types.CallbackQuery):
    await call.answer(cache_time=1)
    await call.message.delete_reply_markup()
    await call.message.answer("Отмена редактирования товара❌",
                              reply_markup=admin_panel_buttons)

    await AdminMenu.adminMenu.set()


async def get_new_name(call: types.CallbackQuery):
    await call.message.edit_text("Введите новое имя для товара📝",
                                 reply_markup=None)

    await RedactProduct.getNewName.set()


async def redact_product_name(message: types.Message, state=FSMContext):
    config = message.bot.get('config')
    data = await state.get_data()
    db = message.bot.get('db')

    product = await db.select_product(product_id=data.get('product_to_redact'))
    bot = message.bot

    await message.answer(f"Новое имя товара {message.text}\n\n"
                         f"<i>для вызова меню используйте:</i> /start")

    await db.redact_product(name=message.text,
                            description=product.get('description'),
                            price=product.get('price'),
                            photo=product.get('photo'),
                            product_id=data.get('product_to_redact'))


async def get_new_description(call: types.CallbackQuery):
    await call.message.delete_reply_markup()
    await call.message.answer("Введите новое описание для товара📝")

    await RedactProduct.getNewDescription.set()


async def redact_product_description(message: types.Message, state: FSMContext):
    config = message.bot.get('config')
    data = await state.get_data()
    db = message.bot.get('db')

    product = await db.select_product(product_id=data.get('product_to_redact'))

    await message.answer(f"Новое описание товара:\n\n {message.text}\n\n"
                         f"<i>для вызова меню используйте:</i> /start")

    await db.redact_product(name=product.get('name'),
                            description=message.text,
                            price=product.get('price'),
                            photo=product.get('photo'),
                            product_id=data.get('product_to_redact'))


async def get_new_price(call: types.CallbackQuery):
    await call.message.delete_reply_markup()
    await call.message.answer("Введите новое цену для товара📝")

    await RedactProduct.getNewPrice.set()


async def redact_product_price(message: types.Message, state: FSMContext):
    config = message.bot.get('config')
    data = await state.get_data()
    db = message.bot.get('db')

    product = await db.select_product(product_id=data.get('product_to_redact'))

    await message.answer(f"Новоя цена товара: {message.text}\n\n"
                         f"<i>для вызова меню используйте:</i> /start")

    await db.redact_product(name=product.get('name'),
                            description=product.get('description'),
                            price=int(message.text),
                            photo=product.get('photo'),
                            product_id=data.get('product_to_redact'))


# PHOTO
# =================================================


async def get_new_photo(call: types.CallbackQuery):
    await call.message.delete_reply_markup()
    await call.message.answer("Пришлите новое фото для товара📷")

    await RedactProduct.getNewPhoto.set()


async def redact_product_photo(message: types.Message, file_uploader: FileUploader, state: FSMContext):
    config = message.bot.get('config')
    db = message.bot.get('db')

    uploaded_photo = await file_uploader.upload_photo(message.photo[-1])
    data = await state.get_data()

    product = await db.select_product(product_id=data.get('product_to_redact'))

    await message.answer_photo(photo=message.photo[-1].file_id,
                               caption=f"Новое фото товара:\n\n"
                                       f"<i>для вызова меню используйте:</i> /start")

    await db.redact_product(name=product.get('name'),
                            description=product.get('description'),
                            price=product.get('price'),
                            photo=uploaded_photo.link,
                            product_id=data.get('product_to_redact'))


def redact_product_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(redact_menu, redact_callback.filter(button="redact_product"),
                                       state=Purchase.selectedProduct)

    dp.register_callback_query_handler(get_new_name, redact_callback.filter(button="change_name"),
                                       state=RedactProduct.changeRedaction)
    dp.register_callback_query_handler(get_new_description, redact_callback.filter(button="change_description"),
                                       state=RedactProduct.changeRedaction)
    dp.register_callback_query_handler(get_new_price, redact_callback.filter(button="change_price"),
                                       state=RedactProduct.changeRedaction)
    dp.register_callback_query_handler(get_new_photo, redact_callback.filter(button="change_photo"),
                                       state=RedactProduct.changeRedaction)
    dp.register_callback_query_handler(cancel_redact, redact_callback.filter(button="cancel"),
                                       state=RedactProduct.changeRedaction),

    dp.register_message_handler(redact_product_name, state=RedactProduct.getNewName)
    dp.register_message_handler(redact_product_description, state=RedactProduct.getNewDescription)
    dp.register_message_handler(redact_product_price, state=RedactProduct.getNewPrice)
    dp.register_message_handler(redact_product_photo, state=RedactProduct.getNewPhoto,
                                content_types=types.ContentType.PHOTO)
