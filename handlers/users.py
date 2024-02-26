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
    # video = open("docs/IMG_0951.MOV", 'rb')
    await message.answer(text=cfg.misc.messages.start, reply_markup=markup)
    await state.finish()
    try:
        pass
    except:
        await message.message.answer(cfg.misc.messages.start, reply_markup=markup)


async def calculate_calory(message: types.Message, state: FSMContext):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']

    user = db.get_user(message.from_user.id)
    await message.answer("Отправьте фотографию для подсчета каллорий.")
    await state.set_state("wait photo")


async def wait_photo(message: types.Message, state: FSMContext):
    kb: Keyboards = ctx_data.get()['keyboards']
    # path = await message.photo[0].download()
    await state.set_state("wait_photo_description")
    await state.update_data(photo=message.photo[0])
    await message.answer("Отправиьте название блюда или описание, для компонентов")


async def wait_photo_description(message: types.Message, state: FSMContext):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']
    photo = await state.get_data("photo")
    path = await photo["photo"].download()
    mes = await message.answer("Веду подсчет...")
    result: str = await calculator.send_photo(path.name, message.text)
    food_data = extract_food_data(result)
    markup = await kb.back_kb("user")
    if food_data.calories != "Неизвестно":
        markup = await kb.add_diary_record_kb(food_data)
    await mes.delete()
    await message.answer(result, reply_markup=markup)
    await state.finish()


async def add_record_to_diary(callback: types.CallbackQuery, state: FSMContext, callback_data: dict):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']
    # callory = callback_data.get("amount")
    # food_data = FoodData(calories=callory)
    dish = callback_data.get("d")
    protein = callback_data.get("pr")
    calories = callback_data.get("cal")
    grams = callback_data.get("gr")
    carbs = callback_data.get("carbs")
    fats = callback_data.get("fats")
    food_data = FoodData(
        dish=dish,
        protein=protein,
        calories=calories,
        grams=grams,
        carbs=carbs,
        fats=fats,

    )

    db.add_diary_record(callback.from_user.id, food_data)
    amount_daily_calory = db.get_amount_daily_records(callback.from_user.id)
    user: User = db.get_user(callback.from_user.id)
    if not user.subscription:
        db.update_free_diary_records(callback.from_user.id)
    await callback.message.answer("Добавлено в дневник")
    if amount_daily_calory > user.daily_calory:
        await callback.message.answer(f"Внимание!!!\nКалорий на сегодня уже достаточно.\n{amount_daily_calory}/{user.daily_calory}")


async def add_record_to_errors(callback: types.CallbackQuery, state: FSMContext, callback_data: dict):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']
    # callory = callback_data.get("amount")
    dish = callback_data.get("d")
    protein = callback_data.get("cal")
    calories = callback_data.get("pr")
    grams = callback_data.get("gr")
    carbs = callback_data.get("carbs")
    fats = callback_data.get("fats")
    food_data = FoodData(
        dish=dish,
        protein=protein,
        calories=calories,
        grams=grams,
        carbs=carbs,
        fats=fats,

    )
    db.add_diary_record(callback.from_user.id, food_data)
    amount_daily_calory = db.get_amount_daily_records(callback.from_user.id)
    user: User = db.get_user(callback.from_user.id)

    await callback.message.answer("Данные об ошибке добавлены.")
    if amount_daily_calory > user.daily_calory:
        await callback.message.answer(f"Внимание!!!\nКалорий на сегодня уже достаточно.\n{amount_daily_calory}/{user.daily_calory}")


async def diary(message: types.Message, state: FSMContext):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']
    user: User = db.get_user(message.from_user.id)
    text = "<b><i>Ваши данные</i></b>:\n"
    await state.finish()
    amount_daily_calory = db.get_amount_daily_records(message.from_user.id)

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

    user = db.get_user(message.from_user.id)
    multiplier = 1 - user.discount/100
    summ = int(399 * multiplier)
    markup = await kb.subscription_kb()
    await message.answer(f"""Премиум Подписка 🌟
Что вы получите: 
1. Доступ к сервису на 1 месяц
2. Возможность по фото определять калорийность блюда 
3. Личный дневник в котором вы будете контролировать ежедневное потребление  калорий

Стоимость месячной подписки: 390 рублей 

В ближайших обновлениях вы также получите:
- Фитнес тренер под рукой. Ответит на все ваши вопросы, составит план тренировок по запросу. 
- Ежедневный мотиватор, будет напоминать о плановых тренировках и давать рекомендации по питанию.""", reply_markup=markup)


async def set_wait_bill(callback: types.CallbackQuery, state: FSMContext):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']

    await state.set_state("wait_bill")
    await callback.message.answer("Отправьте скриншот с чеком об оплате для подтверждения.\
\nЧеки обрабатываются вручную, это может занять некоторое время.")


async def wait_bill(message: types.Message, state: FSMContext):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']
    markup = await kb.confirm_bill_kb(message.from_user.id)
    if message.text is not None:
        await message.bot.send_message(-1002146651809, message.text, reply_markup=markup)
    elif message.photo is not None:
        await message.bot.send_photo(chat_id=-1002146651809, photo=message.photo[-1].file_id,
                                     caption=message.caption, reply_markup=markup)
    elif message.document is not None:
        await message.bot.send_document(chat_id=-1002146651809, document=message.document.file_id,
                                        caption=message.caption, reply_markup=markup)
    markup = await kb.start_kb()
    await state.finish()
    await message.answer("Ваша заявка об оплате отправлена на рассмотрение", reply_markup=markup)


async def confirm_bill(callback: types.CallbackQuery, state: FSMContext, callback_data: dict):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']

    user_id = callback_data.get("user_id")

    match callback_data.get("command"):
        case "confirm":
            db.set_month_subscription(user_id)
            await callback.message.answer("Уведомление отпрвлено")
            await callback.bot.send_message(user_id, "Подписка подтверждена.")
        case "decline":
            await callback.bot.send_message(user_id, "Подписка отклонена, для уточнения причин свяжитесь с @son2421")
            await callback.message.answer("Уведомление об отказе отправлено пользователю, он должен самостоятельно связаться.")
        case "user_info":
            user = db.get_user(user_id)
            await callback.message.answer(f"ID telegram {str(user.user_id)} username: @{user.username}")


async def set_wait_promo_code(callback: types.CallbackQuery, state: FSMContext):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']

    markup = await kb.back_kb("user")
    await state.set_state("wait_promo_code")
    await callback.message.answer("Отправьте промокод", reply_markup=markup)


async def wait_promo_code(message: types.Message, state: FSMContext):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']

    promo = db.get_promo_by_code(message.text)
    if not promo:
        markup = await kb.back_kb("user")
        await message.answer("Такого промокода не существует.\nПопробуйте заново!", reply_markup=markup)
        return
    markup = await kb.subscription_kb()
    db.update_user_discount(message.from_user.id, promo.percent)
    await state.finish()

    await message.answer(f"Промокод успешно применен, за вами закреплена скидка <b>{promo.percent}%</b>.")


async def wait_text(message: types.Message, state: FSMContext):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']
    openai = ctx_data.get()['openai']

    result: str = await _openai.text(message.text, openai)

    await message.answer(result)


async def back(callback: types.CallbackQuery, state: FSMContext):
    cfg: Config = ctx_data.get()['config']
    kb: Keyboards = ctx_data.get()['keyboards']
    db: Database = ctx_data.get()['db']
    data = await state.get_data()
    markup = await kb.start_kb()
    await callback.message.answer(cfg.misc.messages.start, reply_markup=markup)
    await state.finish()


def register_user_handlers(dp: Dispatcher, kb: Keyboards):
    dp.register_message_handler(start, commands=["start"], state="*")
    dp.register_message_handler(diary, regexp="Дневник", state="*")
    dp.register_message_handler(
        calculate_calory, regexp="Подсчет каллорий", state="*")

    dp.register_message_handler(payment, regexp="Подписка", state="*")
    dp.register_callback_query_handler(
        set_wait_promo_code, lambda x: x.data == "set_wait_promo_code", state="*")
    dp.register_message_handler(
        wait_promo_code, state="wait_promo_code")
    dp.register_callback_query_handler(
        set_wait_bill, lambda x: x.data == "set_send_bill", state="*")
    dp.register_message_handler(wait_bill,
                                content_types=[types.ContentType.PHOTO,
                                               types.ContentTypes.PHOTO,
                                               ], state="wait_bill")
    dp.register_callback_query_handler(
        confirm_bill, kb.confirm_bill_cb.filter(), state="*")

    dp.register_message_handler(
        settings, regexp="Ввести свои данные", state="*")
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
    dp.register_callback_query_handler(
        add_record_to_errors, kb.add_dish_to_error_list_cd.filter(), state="*")
    dp.register_callback_query_handler(back, kb.back_cd.filter(), state="*")
    dp.register_message_handler(wait_photo,
                                content_types=[types.ContentType.PHOTO,
                                               types.ContentTypes.PHOTO,
                                               ], state="wait photo")
    dp.register_message_handler(
        wait_photo_description, state="wait_photo_description")

    # dp.register_message_handler(wait_text,
    #                             content_types=[types.ContentType.TEXT,
    #                                            types.ContentTypes.TEXT,
    #                                            ], )
