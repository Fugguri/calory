from typing import List
from aiogram import Bot, types
from models import UserWithWeeklyRecords, UserWithYesterdayRecords

from db import db
from models.models import Record, User
from ._openai import Calculator
from .scheduler import message_scheduler, BaseScheduler


class Message_scheduler():

    def __init__(self, bot: Bot = None) -> None:
        self.db = db
        self.bot: Bot = bot
        self.scheduler: BaseScheduler = message_scheduler
        self.calculator: Calculator = Calculator()

        self.scheduler.start()

    async def start_scheduler(self):
        self.scheduler.add_job(
            self.create_daily_messaging_scheduler,
            'cron', hour=9, minute=0
        )
        # self.scheduler.add_job(
        # self.create_weekly_messaging_scheduler, 'cron', hour=8, minute=0)
        # self.scheduler.add_job(self.test_mailing)

    async def create_daily_messaging_scheduler(self):
        users_with_records: List[UserWithYesterdayRecords] = \
            db.get_user_with_yesterday_records()
        for user_with_records in users_with_records:
            if not user_with_records.user.daily_calory:
                continue
            try:
                text = await self.calculator.create_daily_mail_text(
                    user=user_with_records.user,
                    dish_list=user_with_records.dishes_list
                )

                await self.bot.send_message(
                    chat_id=user_with_records.user.user_id,
                    text=text
                )

            except Exception as ex:
                print(ex)
        else:
            print("Daily mailing done")

    async def create_weekly_messaging_scheduler(self):
        users_with_records: List[UserWithWeeklyRecords] = \
            db.get_user_with_weekly_records()

        for user_with_records in users_with_records:
            if not user_with_records.user.daily_calory:
                continue
            try:
                text = await self.calculator.create_daily_mail_text(
                    user=user_with_records.user,
                    dish_list=user_with_records.dishes_list
                )

                await self.bot.send_message(
                    chat_id=user_with_records.user.user_id,
                    text=text
                )

            except Exception as ex:
                print(ex)
        else:
            print("Weekly mailing done")

    async def test_mailing(self):
        user: User = self.db.get_user(248184623)
        records: List[Record] = self.db.get_amount_daily_records(
            user.user_id)

        try:
            text = await self.calculator.create_weekly_mail_text(
                user=user,
                dish_list=records
            )
            message = await self.bot.send_message(
                chat_id=user.user_id,
                text=text
            )
        except Exception as ex:
            print(ex)
