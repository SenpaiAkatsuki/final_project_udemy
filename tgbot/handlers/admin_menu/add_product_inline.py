import logging

from aiogram import types, Dispatcher
from aiogram.utils.exceptions import ResultIdDuplicate

from tgbot.keyboards.purchase_inline import purchase_keyboard
from tgbot.misc.db_api.postgres_db import Database
from tgbot.misc.states import User, AdminMenu


async def add_product(query: types.InlineQuery):
    items = []
    logging.info("WORKING INLINE")
    config = query.bot.get('config')
    db = query.bot.get('db')

    logging.info("Inline query is: %s", query.query)
    if query.query == '':
        products = await db.get_products()
    else:
        products = await db.get_products_sorted(str(query.query) + '%')

    print(query.query == "")
    print(products)
    for value in products:
        items.append(
            types.InlineQueryResultArticle(
                id=value.get('product_id'),
                input_message_content=types.InputTextMessageContent(
                    message_text=f"{value.get('photo')}\n\n\n"
                                 f"<b>{value.get('name')}</b>\n\n"
                                 f"{value.get('description')}\n\n"
                                 f"Цена: {value.get('price')}💰",
                ),
                title=value.get('name'),
                thumb_url=value.get('photo'),
                description=value.get('description'),
                reply_markup=purchase_keyboard(key=value.get('product_id'))
            ))

    try:
        await query.answer(
            results=items
        )
    except ResultIdDuplicate:
        logging.info(products)
        logging.info("WORKING DUPLICATE")
        pass



def product_inline_query(dp: Dispatcher):
    dp.register_inline_handler(add_product, state=[User.mainMenu, AdminMenu.adminMenu])
