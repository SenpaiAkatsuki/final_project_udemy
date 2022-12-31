from aiogram import types, Dispatcher


async def get_channel_info(message: types.Message):
    await message.answer(f"Сообщение переслано из {message.forward_from_chat.title}\n"
                         f"Username: @{message.forward_from_chat.username}\n"
                         f"ID: {message.forward_from_chat.id}")


async def chat_join_request(message: types.Message):
    await message.bot.approve_chat_join_request(chat_id=-1001480349007,
                                                user_id=message.from_user.id)
    await message.answer(f"Ваша заявка принята\n"
                         f"{await message.bot.export_chat_invite_link(chat_id=-1001480349007)}")


async def chanel_new_member(message: types.Message):
    chat = await message.bot.get_chat(chat_id=-100148034900)
    print(chat['username'])


def register_info_handler(dp: Dispatcher):
    dp.register_message_handler(chanel_new_member, commands=['chat'])
    dp.register_message_handler(get_channel_info, is_forwarded=True, content_types=types.ContentTypes.ANY)
    dp.register_message_handler(chat_join_request, content_types=types.ChatJoinRequest)
