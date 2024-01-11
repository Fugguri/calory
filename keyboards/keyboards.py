from config.config import Config
from aiogram.utils.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, \
    ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from models import *


class Keyboards:
    def __init__(self, cfg: Config) -> None:
        self.text = cfg.misc.buttons_texts
        self.start_cd = CallbackData("start", "character_id")
        self.admin_cd = CallbackData("mailing", "command")
        self.mailing_cd = CallbackData("admin", "command")
        self.add_calory_diary_cd = CallbackData("calory", "amount")
        self.add_dish_to_error_list_cd = CallbackData("dish", "amount")
        self.back_cd = CallbackData("back", "role")

    async def start_kb(self):

        kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
       #  res = []
        kb.add(KeyboardButton(text="Подсчет каллорий"),
               KeyboardButton(text="Дневник"))
        kb.add(KeyboardButton(text="Настройки"),
               KeyboardButton(text="Подписка"))

       #  kb.row(*res)
        return kb

    async def add_diary_record_kb(self, calory_amount):
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton(text="Добавить запись",
               callback_data=self.add_calory_diary_cd.new(amount=calory_amount)))
        kb.add(InlineKeyboardButton(text="Неправильный подсчет грам",
               callback_data=self.add_dish_to_error_list_cd.new(amount=calory_amount)))
        return kb

    async def sex_kb(self):
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton(text="Мужской",
               callback_data="Мужской"))
        kb.add(InlineKeyboardButton(text="Женский",
               callback_data="Женский"))
        kb.add(InlineKeyboardButton(text="Назад",
               callback_data=self.back_cd.new(role='user')))
        return kb

    async def activity_kb(self):
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton(text="Сидячий образ жизни",
               callback_data="Сидячий образ жизни"))
        kb.add(InlineKeyboardButton(text="Низкая",
               callback_data="Низкая"))
        kb.add(InlineKeyboardButton(text="Средняя",
               callback_data="Средняя"))
        kb.add(InlineKeyboardButton(text="Высокая",
               callback_data="Высокая"))
        kb.add(InlineKeyboardButton(text="Очень высокая",
               callback_data="Очень высокая"))
        kb.add(InlineKeyboardButton(text="Назад",
               callback_data=self.back_cd.new(role='user')))
        return kb

    async def goal_kb(self):
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton(text="Набрать вес",
               callback_data="Набрать вес"))
        kb.add(InlineKeyboardButton(text="Снизить вес",
               callback_data="Снизить вес"))
        kb.add(InlineKeyboardButton(text="Поддержание веса",
               callback_data="Поддержание веса"))
        kb.add(InlineKeyboardButton(text="Назад",
               callback_data=self.back_cd.new(role='user')))
        return kb

    async def confirm_settings_kb(self):
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton(text="Данные верны",
               callback_data="Низкая"))
        kb.add(InlineKeyboardButton(text="Средняя",
               callback_data="Средняя"))
        kb.add(InlineKeyboardButton(text="Назад",
               callback_data=self.back_cd.new(role='user')))
        return kb

    async def admin_kb(self):
        kb = InlineKeyboardMarkup()

        kb.add(InlineKeyboardButton(text="Рассылка сообщений",
               callback_data=self.admin_cd.new(command="mail")))
        kb.add(InlineKeyboardButton(text="Статистика",
               callback_data=self.admin_cd.new(command="statistic")))
        kb.add(InlineKeyboardButton(text="Изменить промт",
               callback_data=self.admin_cd.new(command="edit promt")))
        kb.add(InlineKeyboardButton(text="Назад",
               callback_data=self.back_cd.new(role='user')))

        return kb

    async def mailing_kb(self, state: str = None, photo: bool = False):
        kb = InlineKeyboardMarkup()
        if state == "wait_mail_text":
            kb.add(InlineKeyboardButton(text="Назад",
                                        callback_data=self.back_cd.new('admin')))
        if state == 'wait_mail_photo':
            kb.add(InlineKeyboardButton(text="Без фото",
                   callback_data=self.mailing_cd.new("no_photo")))
            if photo:
                kb.add(InlineKeyboardButton(text="Отправить с фото",
                                            callback_data=self.mailing_cd.new("start_with_photo")))
        if state == 'confirm':
            kb.add(InlineKeyboardButton(text="Начать рассылку",
                   callback_data=self.mailing_cd.new("start")))
            kb.add(InlineKeyboardButton(text="Редактировать",
                   callback_data=self.admin_cd.new(command="mail")))
        return kb

    async def back_kb(self, role):
        kb = InlineKeyboardMarkup()

        kb.add(InlineKeyboardButton(text="Назад",
               callback_data=self.back_cd.new(role=role)))

        return kb
