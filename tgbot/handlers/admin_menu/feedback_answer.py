from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from tgbot.keyboards.admin_inline import admin_panel_callback
from tgbot.keyboards.feedback_inilne import answer_feedback_inline, feedback_callback, get_next_feedback_inline, \
    confirm_feedback_answer_inline
from tgbot.misc.states import Feedback, AdminMenu


async def show_feedback(call: types.CallbackQuery, state: FSMContext):
    db = call.bot.get('db')

    reports = await db.select_all_reports()

    query = call.get_current().data

    if not reports:
        if "get_next_feedback" in query:
            await call.message.delete_reply_markup()
            await call.message.answer("Больше нет заявок в поддержку❕\n\n"
                                      "<i>Для вызова меню используйте:</i> /start")

            await AdminMenu.adminMenu.set()
        else:
            await call.answer()
            await call.message.answer("Пока что нет заявок в поддержку❕")
            return
    else:
        await call.message.delete_reply_markup()
        user = await db.select_user(telegram_id=reports[0]['user_id'])
        chat = await call.bot.get_chat(user['telegram_id'])

        await call.message.answer(f'Заявка от пользователя: {chat.get_mention()}')
        if reports[0]['screenshot'] is None:
            await call.message.answer(reports[0]['report'],
                                      reply_markup=answer_feedback_inline)
        else:
            await call.message.answer_photo(reports[0]['screenshot'],
                                            caption=reports[0]['report'],
                                            reply_markup=answer_feedback_inline)
        await state.update_data(
            user_id=reports[0]['user_id']
        )

        await Feedback.answerFeedback.set()


async def catch_feedback_answer(call: types.CallbackQuery):
    await call.message.delete_reply_markup()
    await call.message.answer("Напишите ответ пользователю📝\n\n"
                              "Текст сообщения должен содержать не более 1000 символов❕")

    await Feedback.confirmFeedbackAnswer.set()


async def confirm_feedback_answer(message: types.Message, state: FSMContext):
    if len(message.text) <= 1000:
        await state.update_data(
            answer=message.text
        )
        await message.answer("Отправить ответ пользователю❔")
        await message.answer(f"{message.text}\n\n",
                             reply_markup=confirm_feedback_answer_inline)

        await Feedback.getFeedbackAnswer.set()
    else:
        await message.answer('Неверный формат сообщения❌\n'
                             'сообщение должно содержать меньше 1000 символов')

        await Feedback.confirmFeedbackAnswer.set()


async def send_feedback_answer(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    db = call.message.bot.get('db')

    user = await db.select_user(telegram_id=data.get('user_id'))
    await db.delete_report(user_id=user['telegram_id'])

    await call.message.delete_reply_markup()
    await call.message.bot.send_message(user['telegram_id'],
                                        f"Ваш запрос в поддержку рассмотрен☑️\n"
                                        f"Ответ от администратора <b><code>{call.from_user.full_name}</code></b>:")
    await call.message.bot.send_message(user['telegram_id'],
                                        text=f"{data.get('answer')}")

    await call.message.answer("Ответ отправлен пользователю☑️",
                              reply_markup=get_next_feedback_inline)

    await Feedback.answerFeedback.set()


async def decline_feedback(call: types.CallbackQuery, state: FSMContext):
    db = call.bot.get('db')
    data = await state.get_data()
    user = await db.select_user(telegram_id=data.get('user_id'))

    await call.message.delete_reply_markup()
    await db.delete_report(user_id=user['telegram_id'])
    await call.message.answer("Заявка отклонена❗️",
                              reply_markup=get_next_feedback_inline)


async def exit_feedback_answer(call: types.CallbackQuery):
    await call.message.delete_reply_markup()
    await call.message.answer("Выход из режима ответа на заявки❗️\n\n"
                              "<i>Для вызова меню используйте:</i> /start")

    await AdminMenu.adminMenu.set()


def register_feedback_answer_handler(dp: Dispatcher):
    dp.register_callback_query_handler(show_feedback, feedback_callback.filter(button='get_next_feedback'),
                                       state=Feedback.answerFeedback)
    dp.register_callback_query_handler(show_feedback, admin_panel_callback.filter(button="feedback_answer"),
                                       state=AdminMenu.adminMenu)

    dp.register_message_handler(confirm_feedback_answer,
                                state=Feedback.confirmFeedbackAnswer)

    dp.register_callback_query_handler(catch_feedback_answer,
                                       feedback_callback.filter(button="edit_feedback_answer"),
                                       state=Feedback.getFeedbackAnswer)  # redact feedback version
    dp.register_callback_query_handler(catch_feedback_answer,
                                       feedback_callback.filter(button="answer_feedback"),
                                       state=Feedback.answerFeedback)

    dp.register_callback_query_handler(send_feedback_answer,
                                       feedback_callback.filter(button="send_feedback_answer"),
                                       state=Feedback.getFeedbackAnswer)

    dp.register_callback_query_handler(decline_feedback,
                                       feedback_callback.filter(button="decline_feedback"),
                                       state=Feedback.answerFeedback)
    dp.register_callback_query_handler(exit_feedback_answer,
                                       feedback_callback.filter(button="cancel_feedback"),
                                       state=Feedback.answerFeedback)
