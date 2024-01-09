from aiogram import types
from aiogram import Dispatcher
from aiogram.dispatcher.handler import ctx_data
from aiogram.dispatcher import FSMContext

from .admin import admin
from db import Database
from models import *
from utils import _openai, calculate_calories, extract_food_data
from config.config import Config
from keyboards.keyboards import Keyboards

calculator = _openai.Calculator()


async def start(message: types.Message, state: FSMContext):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']
    try:
        db.get_user(message.from_user.id)
    except:
        db.add_user(message.from_user)

    markup = await kb.start_kb()
    await message.answer(cfg.misc.messages.start, reply_markup=markup)
    try:
        pass
    except:
        await message.message.answer(cfg.misc.messages.start, reply_markup=markup)

    await state.finish()


async def calculate_calory(message: types.Message, state: FSMContext):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']
    await message.answer("Отправьте фотографию для подсчета каллорий.")
    await state.set_state("wait photo")


async def wait_photo(message: types.Message, state: FSMContext):
    kb: Keyboards = ctx_data.get()['keyboards']
    path = await message.photo[0].download()
    result: str = await calculator.send_photo(path.name, message.caption)
    food_data = extract_food_data(result)
    markup = await kb.back_kb("user")
    print(food_data.calories)
    if food_data.calories != "Неизвестно":
        markup = await kb.add_diary_record_kb(food_data.calories)
    await message.answer(result, reply_markup=markup)


async def add_record_to_diary(callback: types.CallbackQuery, state: FSMContext, callback_data: dict):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']
    callory = callback_data.get("amount")
    food_data = FoodData(calories=callory)
    db.add_diary_record(callback.from_user.id, food_data)
    amount_daily_calory = db.get_amount_daily_records()
    user: User = db.get_user(callback.from_user.id)

    await callback.message.answer("Добавлено в дневник")
    if amount_daily_calory > user.daily_calory:
        await callback.message.answer(f"Внимание!!!\nКалорий на сегодня уже достаточно.\n{amount_daily_calory}/{user.daily_calory}")


async def diary(message: types.Message, state: FSMContext):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']
    user: User = db.get_user(message.from_user.id)
    text = "<b><i>Ваши данные</i></b>:\n"

    amount_daily_calory = db.get_amount_daily_records()

    result = text+user.__repr__()
    if amount_daily_calory > user.daily_calory:
        result += f"Внимание!!!\nКалорий на сегодня уже достаточно.\n{amount_daily_calory}/{user.daily_calory}"
    else:
        result += f"\nНабрано сегодня: {amount_daily_calory}/{user.daily_calory}"
    await message.answer(result)


async def settings(message: types.Message, state: FSMContext):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']
    markup = await kb.back_kb("user")
    await message.answer("Введите свой рост", reply_markup=markup)
    await state.set_state('wait height')


async def wait_height(message: types.Message, state: FSMContext):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']
    markup = await kb.back_kb("user")
    await state.update_data(height=message.text)
    await message.answer("Введите свой вес", reply_markup=markup)
    await state.set_state('wait weight')


async def wait_weight(message: types.Message, state: FSMContext):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']
    markup = await kb.back_kb("user")
    await state.update_data(weight=message.text)
    await message.answer("Введите свой возраст", reply_markup=markup)
    await state.set_state('wait age')


async def wait_age(message: types.Message, state: FSMContext):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']
    await state.update_data(age=message.text)
    markup = await kb.sex_kb()
    await message.answer("Выберите свой пол", reply_markup=markup)
    await state.set_state('wait sex')


async def wait_sex(callback: types.CallbackQuery, state: FSMContext):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']
    markup = await kb.activity_kb()
    await state.update_data(sex=callback.data)
    await callback.message.answer("Выберите вашу активность", reply_markup=markup)
    await state.set_state('wait activity')


async def wait_activity(callback: types.CallbackQuery, state: FSMContext):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']
    markup = await kb.goal_kb()
    await state.update_data(activity=callback.data)
    await callback.message.answer("Выберите цель", reply_markup=markup)
    await state.set_state('wait goal')


async def wait_goal(callback: types.CallbackQuery, state: FSMContext):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']
    markup = await kb.confirm_settings_kb()
    await state.update_data(goal=callback.data)
    data = await state.get_data()
    setting = Settings(**data)
    await callback.message.answer(f"Подтвердите данные:\n{setting.__repr__()}", reply_markup=markup)
    await state.set_state('confirm settings')


async def confirm_settings(callback: types.CallbackQuery, state: FSMContext):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']
    data = await state.get_data()
    settings = Settings(**data)
    calory = calculate_calories(settings)
    db.update_user_data(callback.from_user.id, settings)
    db.update_daily_calory(callback.from_user.id, calory)
    await callback.message.answer(f"Дневная норма - {calory}")
    await state.finish()


async def payment(message: types.Message, state: FSMContext):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']
    await message.answer("Тут будет оплата.")


async def wait_text(message: types.Message, state: FSMContext):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']
    openai = ctx_data.get()['openai']

    result: str = await _openai.text(message.text, openai)

    await message.answer(result)


def register_user_handlers(dp: Dispatcher, kb: Keyboards):
    dp.register_message_handler(start, commands=["start"], state="*")
    dp.register_message_handler(
        calculate_calory, regexp="Подсчет каллорий", state="*")
    dp.register_message_handler(diary, regexp="Дневник", state="*")
    dp.register_message_handler(payment, regexp="Оплата", state="*")
    dp.register_message_handler(settings, regexp="Настройки", state="*")
    dp.register_message_handler(wait_height, state="wait height")
    dp.register_message_handler(wait_weight, state="wait weight")
    dp.register_message_handler(wait_age, state="wait age")
    dp.register_callback_query_handler(wait_sex, state="wait sex")
    dp.register_callback_query_handler(wait_goal, state="wait goal")
    dp.register_callback_query_handler(wait_activity, state="wait activity")
    dp.register_callback_query_handler(
        confirm_settings, state="confirm settings")
    dp.register_callback_query_handler(
        add_record_to_diary, kb.add_calory_diary_cd.filter(), state="*")

    dp.register_message_handler(wait_photo,
                                content_types=[types.ContentType.PHOTO,
                                               types.ContentTypes.PHOTO,
                                               ], state="wait photo")
    # dp.register_message_handler(wait_text,
    #                             content_types=[types.ContentType.TEXT,
    #                                            types.ContentTypes.TEXT,
    #                                            ], )
