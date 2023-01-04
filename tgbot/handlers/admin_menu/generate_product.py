import re
from random import randint

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from tgbot.integrations.telegraph import FileUploader
from tgbot.keyboards.admin_inline import admin_panel_callback, product_creation_cancel, cancel_callback, \
    admin_panel_buttons
from tgbot.misc.states import AdminMenu, CreateProduct


async def start_create_product(call: CallbackQuery):
    await call.answer()

    await call.message.answer("🖍Введите кодовое слово продукта\n\n"
                              "<b>❗️код устанавливается один раз, редактировать в будущем не получится❗️</b>",
                              reply_markup=product_creation_cancel)

    await call.message.delete_reply_markup()

    await CreateProduct.start_creation.set()


async def catch_id(message: types.Message, state: FSMContext):
    pattern = re.compile(r'^[a-z,A-Z]{1,64}$')  # 1-64 latin letters
    db = message.bot.get("db")
    products = await db.get_products()

    if pattern.match(message.text):
        for i in products:
            if message.text in products[0]['product_id']:
                await message.answer("Такой продукт уже существует❌\n\n"
                                     "Пришлите кодовое слово еще раз",
                                     reply_markup=product_creation_cancel)

                await message.bot.edit_message_reply_markup(chat_id=message.from_user.id,
                                                            message_id=message.message_id - 1,
                                                            reply_markup=None)
            else:
                await message.bot.edit_message_text(chat_id=message.from_user.id,
                                                    message_id=message.message_id - 1,
                                                    text=f"Кодовое слово☑️️",
                                                    reply_markup=None)

                await state.update_data(
                    {
                        "tag": message.text
                    }
                )

                await message.answer("🖍Введите <b>титульное имя</b> товара\n",
                                     reply_markup=product_creation_cancel)

                await CreateProduct.step_id.set()

    else:
        await message.answer("Неверный формат❌\n\n"
                             "Пришлите кодовое слово еще ра\n\n"
                             "<b>используйте только латинские символы</b>",
                             reply_markup=product_creation_cancel)

        await message.bot.edit_message_reply_markup(chat_id=message.from_user.id,
                                                    message_id=message.message_id - 1,
                                                    reply_markup=None)
        await CreateProduct.start_creation.set()


async def catch_name(message: types.Message, state: FSMContext):
    if message.text:
        await state.update_data(
            {
                "name": message.text
            }
        )

        await message.bot.edit_message_text(chat_id=message.from_user.id,
                                            message_id=message.message_id - 1,
                                            text=f"Титульное имя☑️\n\n",
                                            reply_markup=None)

        await message.answer("🖍Введите <b>описание</b> товара",
                             reply_markup=product_creation_cancel)

        await CreateProduct.step_name.set()
    else:
        await message.answer("Неверный формат❌\n\n"
                             "Пришлите титульное имя еще раз",
                             reply_markup=product_creation_cancel)

        await message.bot.edit_message_reply_markup(chat_id=message.from_user.id,
                                                    message_id=message.message_id - 1,
                                                    reply_markup=None)

        await CreateProduct.step_id.set()


async def catch_description(message: types.Message, state: FSMContext):
    pattern = re.compile(r'^.{1,255}$') # 1-255 symbols

    if pattern.match(message.text):
        await message.bot.edit_message_text(chat_id=message.from_user.id,
                                            message_id=message.message_id - 1,
                                            text=f"Описание☑️",
                                            reply_markup=None)

        await state.update_data(
            {
                "description": message.text
            }
        )

        await message.answer("🖍Введите <b>цену</b> для товара",
                             reply_markup=product_creation_cancel)

        await CreateProduct.step_description.set()
    else:
        await message.answer("Неверный формат❌\n\n"
                             "До 255 символов",
                             reply_markup=product_creation_cancel)

        await message.bot.edit_message_reply_markup(chat_id=message.from_user.id,
                                                    message_id=message.message_id - 1,
                                                    reply_markup=None)

        await CreateProduct.step_name.set()


async def catch_price(message: types.Message, state: FSMContext):
    pattern = re.compile(r'^\d{1,10}$')  # 1-10 digits

    if pattern.match(message.text):
        await state.update_data(
            {
                "price": message.text
            }
        )

        await message.bot.edit_message_text(chat_id=message.from_user.id,
                                            message_id=message.message_id - 1,
                                            text=f"Цена☑️",
                                            reply_markup=None)

        await message.answer("📷Пришлите фото товара",
                             reply_markup=product_creation_cancel)

        await CreateProduct.step_price.set()

    else:
        await message.answer("Некорректная цена❌\n\n"
                             "Попробуйте еще раз",
                             reply_markup=product_creation_cancel)

        await message.bot.edit_message_reply_markup(chat_id=message.from_user.id,
                                                    message_id=message.message_id - 1,
                                                    reply_markup=None)

        await CreateProduct.step_description.set()


async def end_creation_product(message: types.Message, file_uploader: FileUploader, state: FSMContext):
    db = message.bot.get('db')

    if message.photo:
        photo = message.photo[-1]

        uploaded_photo = await file_uploader.upload_photo(photo)
        await state.update_data(
            {
                "photo": uploaded_photo.link
            }
        )
        await message.bot.edit_message_text(chat_id=message.from_user.id,
                                            message_id=message.message_id - 1,
                                            text=f"Фото☑️",
                                            reply_markup=None)

        data = await state.get_data()

        await db.create_product(product_id=data.get('tag'),
                                name=data.get('name'),
                                description=data.get('description'),
                                price=int(data.get('price')),
                                photo=data.get('photo'),
                                quantity=randint(1, 100)
                                )

        await message.answer(text="Товар успешно добавлен☑️\n"
                                  "<b>Появление товара в каталоге может занят несколько минут</b>",
                             reply_markup=admin_panel_buttons)

        await AdminMenu.adminMenu.set()
    else:
        await message.answer("Неверный формат❌\n\n"
                             "Пришлите фото товара в формате <b>jpg</b> или <b>png</b>",
                             reply_markup=product_creation_cancel)

        await message.bot.edit_message_reply_markup(chat_id=message.from_user.id,
                                                    message_id=message.message_id - 1,
                                                    reply_markup=None)
        await CreateProduct.step_price.set()


async def cancel_product_creation(call: CallbackQuery):
    await call.message.delete_reply_markup()
    await call.message.answer(f"<b>Меню администратора📀</b>\n\n"
                              f"❌<b>Создание товара отменено</b>❌",
                              reply_markup=admin_panel_buttons)

    await AdminMenu.adminMenu.set()


def register_inlineMode_handler_admin(dp: Dispatcher):
    dp.register_callback_query_handler(cancel_product_creation, cancel_callback.filter(button="cancel_action"),
                                       state="*")
    dp.register_callback_query_handler(start_create_product, admin_panel_callback.filter(button="add_product"),
                                       state=AdminMenu.adminMenu)

    dp.register_message_handler(catch_id, state=CreateProduct.start_creation,
                                content_types=types.ContentTypes.ANY)
    dp.register_message_handler(catch_name, state=CreateProduct.step_id,
                                content_types=types.ContentTypes.ANY)
    dp.register_message_handler(catch_description, state=CreateProduct.step_name,
                                content_types=types.ContentTypes.ANY)
    dp.register_message_handler(catch_price, state=CreateProduct.step_description,
                                content_types=types.ContentTypes.ANY)
    dp.register_message_handler(end_creation_product,
                                state=CreateProduct.step_price,
                                content_types=types.ContentTypes.ANY)
