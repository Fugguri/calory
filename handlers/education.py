from .users import user_food_data
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


async def go_educate(callback: types.CallbackQuery, state: FSMContext):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']
    markup = await kb.back_kb("user")
    await callback.message.answer("Как мне к тебе обращаться?", reply_markup=markup)
    await state.set_state('educate wait name')


async def educate_wait_name(message: types.Message, state: FSMContext):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']
    markup = await kb.back_kb("user")
    await state.update_data(name=message.text)
    await message.answer("Сколько тебе полных лет?", reply_markup=markup)
    await state.set_state('educate wait age')


async def educate_wait_age(message: types.Message, state: FSMContext):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']
    markup = await kb.back_kb("user")
    await state.update_data(age=message.text)
    await message.answer("Какой у тебя рост в сантиметрах?", reply_markup=markup)
    await state.set_state('educate wait height')


async def educate_wait_height(message: types.Message, state: FSMContext):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']
    markup = await kb.back_kb("user")
    await state.update_data(height=message.text)
    await message.answer("Какой у тебя весь в кг?", reply_markup=markup)
    await state.set_state('educate wait weight')


async def educate_wait_weight(message: types.Message, state: FSMContext):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']
    await state.update_data(weight=message.text)
    markup = await kb.sex_kb()
    await message.answer("Выбери свой пол", reply_markup=markup)
    await state.set_state('educate wait sex')


async def educate_wait_sex(callback: types.CallbackQuery, state: FSMContext):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']
    markup = await kb.activity_kb()
    await state.update_data(sex=callback.data)
    await callback.message.answer("Выбери уровень своей активности", reply_markup=markup)
    await state.set_state('educate wait activity')


async def educate_wait_activity(callback: types.CallbackQuery, state: FSMContext):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']
    markup = await kb.goal_kb()
    await state.update_data(activity=callback.data)
    await callback.message.answer("Какая у тебя цель?", reply_markup=markup)
    await state.set_state('educate wait goal')


async def educate_wait_goal(callback: types.CallbackQuery, state: FSMContext):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']
    markup = await kb.confirm_settings_kb()
    await state.update_data(goal=callback.data)
    data = await state.get_data()
    setting = Settings(**data)
    await callback.message.answer(f"Подтвердите данные:\n{setting.__repr__()}", reply_markup=markup)
    await state.set_state('educate confirm settings')


async def educate_confirm_settings(callback: types.CallbackQuery, state: FSMContext):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']
    data = await state.get_data()
    settings = Settings(**data)
    calory = calculate_calories(settings)
    db.update_user_data(callback.from_user.id, settings)
    db.update_daily_calory(callback.from_user.id, calory)
    markup = await kb.education_count_callory_kb()
    await callback.message.answer(
        (
            '''Отлично!\n
Ты сделал(а) важный шаг к здоровому образу жизни!
Давай попробуем что-то веселое и полезное:
Сфотографируй свое следующее блюдо.
Нажми кнопку "Подсчёт калорий".
Я расскажу тебе всё о калорийности и составе блюда.
Это поможет тебе:
Сознательно подходить к выбору продуктов.
Контролировать свое питание.
Тебе не нужно ничего делать, кроме как фотографировать еду!
Давай начнем!
Нажми на кнопку "Подсчёт калорий".
Присылай свое первое фото.
Вместе мы сделаем твою мечту реальностью!'''

        ),
        reply_markup=markup
    )
    await state.finish()


async def educate_count_callory_photo(callback: types.CallbackQuery, state: FSMContext):
    kb: Keyboards = ctx_data.get()['keyboards']
    await state.set_state('educate wait photo')
    await callback.message.answer("Отправь фото для анализа БЖУ.")


async def educate_wait_photo(message: types.Message, state: FSMContext):
    kb: Keyboards = ctx_data.get()['keyboards']

    # path = await message.photo[0].download()

    await state.update_data(photo=message.photo[0])

    await message.answer('Отлично! Спасибо за фото! 📸 Чтобы повысить точность анализа, пришли, пожалуйста, несколько слов с описанием блюда. Например, если это "овощной салат" или "куриный суп", просто укажи это. Это поможет мне сделать анализ калорийности и питательной ценности ещё более точным. Жду твоего описания! 🥗🍲')

    await state.set_state("educate wait_photo_description")


async def educate_wait_photo_description(message: types.Message, state: FSMContext):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']
    photo = await state.get_data("photo")
    path = await photo["photo"].download()
    mes = await message.answer("Веду подсчет...")
    print(message.from_user.id)
    try:
        user: User = db.get_user(message.from_user.id)
    except:
        markup = await kb.wait_user_data_kb()
        await message.answer("Невозможно получить данные.Пройдите регистрацию заново.", reply_markup=markup)
        return
    result: str = await calculator.send_photo(path.name, message.text, user.daily_calory)
    print(result)
    food_data = extract_food_data(result)
    user_food_data[message.from_user.id] = food_data
    markup = await kb.back_kb("user")
    if food_data.calories != "Неизвестно":
        markup = await kb.add_diary_record_kb(food_data)
    text = await calculator.create_educate_answer(food_data=food_data, user=user)
    await message.answer(text, reply_markup=markup)
    await mes.delete()
    # await message.answer(result+'\nВы получили БЖУ. Чтобы дабавить данные в дневник питания - нажмите кнопку "Добавить запись ', reply_markup=markup)
    markup = await kb.start_kb()

    await message.answer(f'У вас осталось {user.free_diary_records} бесплатных попыток.\n Вы успешно прошли инструкцию как пользоваться ботом SlimFoto.\n\nЧтобы приобрести подписку нажмите на кнопку "Подписка"', reply_markup=markup)


def register_education_handlers(dp: Dispatcher, kb: Keyboards):

    dp.register_callback_query_handler(
        go_educate, lambda x: x.data == "wait_user_data", state="*")
    dp.register_message_handler(
        educate_wait_name, state="educate wait name")
    dp.register_message_handler(educate_wait_age, state="educate wait age")
    dp.register_message_handler(
        educate_wait_height, state="educate wait height")
    dp.register_message_handler(
        educate_wait_weight, state="educate wait weight")
    dp.register_callback_query_handler(
        educate_wait_sex, state="educate wait sex")
    dp.register_callback_query_handler(
        educate_wait_goal, state="educate wait goal")
    dp.register_callback_query_handler(
        educate_wait_activity, state="educate wait activity")
    dp.register_callback_query_handler(
        educate_confirm_settings, state="educate confirm settings")
    # dp.register_callback_query_handler(
    #     educate_add_record_to_diary, kb.add_calory_diary_cd.filter(), state="*")
    # dp.register_callback_query_handler(
    #     add_record_to_errors, kb.add_dish_to_error_list_cd.filter(), state="*")
    dp.register_callback_query_handler(
        educate_count_callory_photo, lambda x: x.data == "education_count_callory", state="*")

    dp.register_message_handler(educate_wait_photo,
                                content_types=[types.ContentType.PHOTO,
                                               types.ContentTypes.PHOTO,
                                               ], state="educate wait photo")
    dp.register_message_handler(
        educate_wait_photo_description, state="educate wait_photo_description")
