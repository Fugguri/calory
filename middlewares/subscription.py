from db import db
from datetime import date

from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware


def is_subscription(user_id: int):
    today = date.today()
    user = db.get_user(user_id)
    if not user.subscription:
        return False
    if today > user.subscription:
        return False
    return True


def is_have_free_diary_records(user_id: int):
    user = db.get_user(user_id)
    if user.free_diary_records > 0:
        return True
    return False


class SubscriptionMiddleware(BaseMiddleware):

    def __init__(self):
        super().__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        # if message.text == "Подсчет каллорий":

        #     subscription = is_subscription(message.from_user.id)
        #     if not subscription and is_have_free_diary_records(message.from_user.id):
        #         return

        #     if not subscription:
        #         await message.answer(text='Чтобы пользоваться сервисом приобретите подписку.\
        #             \nДля того чтобы приобрести подписку перейдите по кнопке "Подписка"')
        #         raise CancelHandler()
