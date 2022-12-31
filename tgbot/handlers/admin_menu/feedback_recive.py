from datetime import date

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from tgbot.keyboards.feedback_inilne import confirm_feedback_inline, feedback_callback
from tgbot.misc.states import AdminMenu, User


class Feedback(StatesGroup):
    confirmFeedback = State()
    getFeedback = State()


async def get_feedback(call: types.CallbackQuery):
    await call.message.delete_reply_markup()
    await call.message.answer("Опишите вашу проблему📝")

    await Feedback.confirmFeedback.set()


async def confirm_feedback(message: types.Message, state: FSMContext):
    await message.answer(f"Отправить сообщение в поддержку?\n\n"
                         f"{message.text}",
                         reply_markup=confirm_feedback_inline)

    await state.update_data(
        feedback=message.text,
        from_user=message.from_user.full_name,
        time=date.today().strftime("%d/%m/%Y"),
        user_mention=message.from_user.get_mention()
    )

    await Feedback.getFeedback.set()


async def submit_feedback(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    config = call.bot.get('config')

    await call.message.delete_reply_markup()
    await call.message.answer(f'Сообщение отправлено в поддержку вскоре вы получите ответ☑️\n\n'
                              f'<i>Для вызова меню используйте:</i> /start')

    for sup in config.tg_bot.supports:
        await call.bot.send_message(sup,
                                    f"Прислал: {data.get('user_mention')}\n"
                                    f"дата сообщения🗓 <b>{data.get('time')}</b>\n\n"
                                    f"{data.get('feedback')}")

    await User.mainMenu.set()


def register_feedback_receive_handler(dp: Dispatcher):
    dp.register_callback_query_handler(get_feedback,
                                       feedback_callback.filter(button="call_support"),
                                       state=[User.mainMenu, AdminMenu.adminMenu])
    dp.register_message_handler(confirm_feedback,
                                state=Feedback.confirmFeedback)
    dp.register_callback_query_handler(submit_feedback,
                                       feedback_callback.filter(button="send_feedback"),
                                       state=Feedback.getFeedback)
