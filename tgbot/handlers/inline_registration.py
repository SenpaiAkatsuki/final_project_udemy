from aiogram import types, Dispatcher


async def empty_query(query: types.InlineQuery):
    config = query.bot.get('config')
    if query.from_user.id not in config.misc.allowed_users:
        await query.answer(
            results=[],
            switch_pm_text="Запустить бота?",
            switch_pm_parameter="registration",
            cache_time=2
        )
        return


def RegistrationInline_handler(dp: Dispatcher):
    dp.register_inline_handler(empty_query)
