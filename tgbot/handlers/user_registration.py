from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.markdown import bold

from tgbot.keyboards.admin_inline import admin_main_menu
from tgbot.keyboards.main_menu_inline import main_menu_keyboard
from tgbot.keyboards.user_start_inline import user_callback, cancel_keyboard, verification_buttons
from tgbot.misc import subscription
from tgbot.misc.db_api.postgres_db import Database
from tgbot.misc.rate_limit import rate_limit
from tgbot.misc.states import User, Code_check, AdminMenu


@rate_limit(limit=3)
async def user_start(message: Message, state: FSMContext):
    # try:
    config = message.bot.get('config')
    db = message.bot.get('db')
    allowed_users = []

    chat = await message.bot.get_chat(chat_id=-1001480349007)
    arguments = message.get_args()
    list_of_telegram_id = await db.get_telegram_id()

    for user_id in list_of_telegram_id:
        allowed_users.append(user_id[0])

    if message.from_user.id in allowed_users:
        if message.from_user.id in config.tg_bot.admin_ids:
            await message.answer("Welcome back <b>admin</b>",
                                 reply_markup=admin_main_menu)
            await AdminMenu.adminMenu.set()
        else:
            await message.answer("Welcome back",
                                 reply_markup=main_menu_keyboard)
            await User.mainMenu.set()

    elif arguments:
        users_referrals = await db.get_telegram_id()
        product_id = await db.get_product_id()
        for referral_id in users_referrals:
            if arguments == str(referral_id[0]):
                user = await db.select_user(telegram_id=int(arguments))
                await db.add_user(
                    telegram_id=message.from_user.id,
                    username=message.from_user.username,
                    referral_id=referral_id[0]
                )
                await message.answer(f"Бот запущен! Вы приняли приглашение от @{user['username']}")
                await message.answer("Добро пожаловать в <b>главное меню</b>\n\n"
                                     "На ваш баланс зачислено <b>100💰</b>",
                                     reply_markup=main_menu_keyboard)

                await db.change_user_balance(100,
                                             message.from_user.id)

                referral = await db.select_user(telegram_id=referral_id[0])

                await db.change_user_balance(referral['balance'] + 100, referral_id[0])

                await message.bot.send_message(chat_id=referral_id[0],
                                               text=f"Пользователь @{message.from_user.username}"
                                                    f" принял ваше приглашение! На ваш баланс зачислено <b>100💰</b>")

                await User.mainMenu.set()
                break

            elif arguments == "registration":
                if message.from_user.id in allowed_users:
                    if message.from_user.id in config.tg_bot.admin_ids:
                        await message.answer("Welcome back <b>admin</b>",
                                             reply_markup=admin_main_menu)
                        await AdminMenu.adminMenu.set()
                    else:
                        await message.answer("Welcome back",
                                             reply_markup=main_menu_keyboard)
                        await User.mainMenu.set()
                else:
                    await message.reply(f"Пройдите регистрацию в боте для получения доступа💮\n"
                                        f"Перейдите по реферальной ссылке или же введите секретный код\n\n"
                                        f"Нет приглашения? Тогда просто подпишись на канал @{chat['username']}"
                                        f" для получения доступа к боту",
                                        reply_markup=verification_buttons)
                    await User.untilApproved.set()

            else:
                await message.answer("Для начала нужно пройти регистрацию: /start")
    else:
        await message.reply(f"❗️Бот доступен только по приглашению❗\n"
                            f"Перейдите по реферальной ссылке или же введите секретный код\n\n"
                            f"Нет приглашения? Тогда просто подпишись на канал @{chat['username']}"
                            f" для получения доступа к боту",
                            reply_markup=verification_buttons)
        await User.untilApproved.set()


async def check_subscription_to_chanel(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=2)
    result = str()
    config = call.bot.get('config')
    db = call.bot.get('db')

    for channel in config.channel.channel_id:
        status = await subscription.check_subscription(user_id=call.from_user.id,
                                                       channel=channel)
        if status:
            result += f"Подписка на канал {bold('Оформлена')}!\n\n"
            await call.message.answer("Добро пожаловать в главное меню",
                                      reply_markup=main_menu_keyboard)
            await db.add_user(
                username=call.from_user.username,
                telegram_id=call.from_user.id
            )
            await User.mainMenu.set()
        else:
            invite_link = await call.bot.export_chat_invite_link(chat_id=channel)
            result += f"Подписка на канал {bold('не оформлена')}!"
            await User.untilApproved.set()
    await call.message.edit_text(result, reply_markup=None)


async def check_invite(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=2)
    await call.message.edit_text("Пришлите код приглашение",
                                 reply_markup=cancel_keyboard)
    await Code_check.Q1.set()


async def check_invite_code_approve(message: Message):
    config = message.bot.get('config')
    db = message.bot.get('db')

    if message.text == config.misc.secret_code:
        await db.add_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username
        )
        await message.answer(f"Доступ получен✅!")
        await message.answer("Добро пожаловать в главное меню",
                             reply_markup=main_menu_keyboard)

        await User.mainMenu.set()
    else:
        await message.reply("Неверный код❌\n"
                            "Проверьте правильно ли вы указали все цифры <b>(без пробелов и символов)</b>")

        await Code_check.Q1.set()


async def cancel_menu(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=2)
    chat = await call.bot.get_chat(chat_id=-1001480349007)
    await call.message.edit_text(f"❗Перед использованием бота нужно подтвердить регистрацию❗\n"
                                 f"Подпишитесь на этот канал: @{chat['username']}\n"
                                 f"После нажмите кнопку проверки подписки\n\n"
                                 f"Либо введите код приглашения",
                                 reply_markup=verification_buttons)
    await User.untilApproved.set()


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=["start"], state="*")
    dp.register_message_handler(check_invite_code_approve, state=Code_check.Q1)
    dp.register_callback_query_handler(check_subscription_to_chanel,
                                       user_callback.filter(type="member_check"),
                                       state=User.untilApproved)
    dp.register_callback_query_handler(check_invite,
                                       user_callback.filter(type="invite_code"),
                                       state=User.untilApproved)
    dp.register_callback_query_handler(cancel_menu,
                                       user_callback.filter(type="cancel"),
                                       state="*")
