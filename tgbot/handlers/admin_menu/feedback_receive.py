from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from tgbot.keyboards.feedback_inilne import confirm_feedback_inline, feedback_callback
from tgbot.misc.states import AdminMenu, User, Feedback


async def get_feedback(call: types.CallbackQuery):
    db = call.bot.get('db')
    reports = await db.select_all_reports()

    for record in reports:
        if call.from_user.id == record['user_id']:
            await call.answer(cache_time=1)
            await call.message.answer("Вы уже отправили заявку в поддержку, ожидайте ответа⌛️")
            return

    await call.message.delete_reply_markup()
    await call.message.answer("Опишите вашу проблему📝\n\n"
                              "Текст сообщения должен содержать не более 1000 символов❕\n\n"
                              "В случае если вы хотите прикрепить фото, просто пришлите текст вместе с фото📷")

    await Feedback.confirmFeedback.set()


async def confirm_feedback_report(message: types.Message, state: FSMContext):
    data = await state.get_data()
    dp = message.bot.get('dp')

    if message.text or message.photo:
        if message.photo:
            if len(message.caption) <= 1000:
                await message.answer("Отправить сообщение в поддержку?")
                await state.update_data(
                    feedback=message.caption,
                    screenshot=message.photo[-1].file_id
                )
                await message.answer_photo(caption=f"{message.caption}",
                                           photo=message.photo[-1].file_id,
                                           reply_markup=confirm_feedback_inline)
                await Feedback.sendFeedback.set()
            else:
                await message.answer('Неверный формат сообщения❌\n'
                                     'сообщение должно содержать меньше 1000 символов')
                await Feedback.confirmFeedback.set()
        else:
            if len(message.text) <= 1000:
                await message.answer("Отправить сообщение в поддержку?")
                await state.update_data(
                    feedback=message.text,
                )
                await message.answer(f"{message.text}",
                                     reply_markup=confirm_feedback_inline)

                await Feedback.sendFeedback.set()
            else:
                await message.answer('Неверный формат сообщения❌\n'
                                     'сообщение должно содержать меньше 1000 символов')
                await Feedback.confirmFeedback.set()
    else:
        await message.answer('Неверный формат сообщения❌')
        await Feedback.confirmFeedback.set()


async def submit_feedback(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    db = call.bot.get('db')

    await call.message.delete_reply_markup()
    if data.get('screenshot'):
        await db.add_report(user_id=call.from_user.id,
                            report=data.get('feedback'),
                            screenshot=data.get('screenshot'))
    else:
        await db.add_report(user_id=call.from_user.id,
                            report=data.get('feedback'))

    await call.message.answer(f'Заявка отправлена в поддержку, вскоре вы получите ответ☑️\n\n'
                              f'<i>Для вызова меню используйте:</i> /start')

    await User.mainMenu.set()


def register_feedback_receive_handler(dp: Dispatcher):
    dp.register_callback_query_handler(get_feedback,
                                       feedback_callback.filter(button="call_support"),
                                       state=[User.mainMenu, AdminMenu.adminMenu])
    dp.register_message_handler(confirm_feedback_report,
                                state=Feedback.confirmFeedback,
                                content_types=types.ContentTypes.ANY)
    dp.register_callback_query_handler(submit_feedback,
                                       feedback_callback.filter(button="send_feedback"),
                                       state=Feedback.sendFeedback)
