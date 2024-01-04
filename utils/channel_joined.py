from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from cachetools import TTLCache


channel_joined_member_cache = TTLCache(maxsize=1000, ttl=300)


def is_member_in_channel(member: types.ChatMember) -> bool:
    if member.status == "left" or member.status == "kicked" or member.status == "restricted":
        return False
    return True


async def get_channel_member(channel_id:int, message: types.Message) -> types.ChatMember:
    
    return await message.bot.get_chat_member(channel_id, message.from_user.id)


async def get_cache_channel_member(channel_id: int, message: types.Message) -> types.ChatMember:
    chat_id = message.from_user.id

    if chat_id in channel_joined_member_cache:
        return channel_joined_member_cache[chat_id]

    member = await get_channel_member(channel_id, message)

    if is_member_in_channel(member):
        channel_joined_member_cache[chat_id] = member

    return member

async def on_process_message(self, message: types.Message, data: dict):
        if message.text != "/start":
            all_joined = True
            channels_text=""
            for key, value in self.json.get_channels().items():
                member = await get_channel_member(key, message)
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(text="Проверить подписку",callback_data="check"))
                if not is_member_in_channel(member):
                    all_joined = False
                    channels_text +="\n"+value
            if not all_joined:            
                await message.answer(text=f"Чтобы пользоваться сервисом - подпишитесь {channels_text} ",
                                            reply_markup=markup)
                raise CancelHandler()



class ChannelJoinedMiddleware(BaseMiddleware):
    def __init__(self,js ):
        super().__init__()
        self.json = js

    async def on_process_message(self, message: types.Message, data: dict):
        if message.text != "/start":
            all_joined = True
            channels_text=""
            for key, value in self.json.get_channels().items():
                member = await get_channel_member(key, message)
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(text="Проверить подписку",callback_data="check"))
                if not is_member_in_channel(member):
                    all_joined = False
                    channels_text +="\n"+value
            if not all_joined:            
                await message.answer(text=f"Чтобы пользоваться сервисом - подпишитесь {channels_text} ",
                                            reply_markup=markup)
                raise CancelHandler()
