from .exelWriter import ExcelWriter
import re
from .channel_joined import *
from .text_to_speech import *
from .texts import Texts
from models import Settings, FoodData
create_text = Texts()
is_member_in_channel


def calculate_calories(settings: Settings):
    # Constants for Harris-Benedict equation
    if settings.sex == 'Мужской':
        bmr = 88.362 + (13.397 * float(settings.weight)) + \
            (4.799 * float(settings.height)) - (5.677 * float(settings.age))
    elif settings.sex == 'Женский':
        bmr = 447.593 + (9.247 * float(settings.weight)) + \
            (3.098 * float(settings.height)) - (4.330 * float(settings.age))

    # Adjust BMR based on activity level
    activity_levels = {
        'Сидячий образ жизни': 1.2,
        'Низкая': 1.375,
        'Средняя': 1.55,
        'Высокая': 1.725,
        'Очень высокая': 1.9
    }

    if settings.activity in activity_levels:
        total_calories = bmr * activity_levels[settings.activity]
    return int(total_calories)


def extract_food_data(text_message):
    # Используем регулярные выражения для извлечения данных
    dish_match = re.search(r'Блюдо: (\d+)', text_message)
    protein_match = re.search(r'Белки: (\d+)', text_message)
    carbs_match = re.search(r'Углеводы: (\d+)', text_message)
    fats_match = re.search(r'Жиры: (\d+)', text_message)
    calories_match_1 = re.search(r'Калории: (\d+)', text_message)
    calories_match_2 = re.search(r'Калории: (\d+)-(\d+)', text_message)
    grams_match = re.search(r'Грамм: (\d+)', text_message)
    average_calories = None

    if calories_match_2:
        min_calories = int(calories_match_2.group(1))
        max_calories = int(calories_match_2.group(2))
        average_calories = int((min_calories + max_calories) // 2)
    elif calories_match_1:
        average_calories = int(calories_match_1.group(1)
                               ) if calories_match_1 else None

    # Создаем экземпляр датакласса
    food_data = FoodData(
        dish=dish_match.group(1) if dish_match else "Неизвестно",
        protein=protein_match.group(1) if protein_match else "Неизвестно",
        calories=average_calories if average_calories else "Неизвестно",
        grams=grams_match.group(1) if grams_match else "Неизвестно",
        carbs=carbs_match.group(1) if carbs_match else "Неизвестно",
        fats=fats_match.group(1) if fats_match else "Неизвестно",
    )

    return food_data


exel_writer = ExcelWriter()

__all__ = [
    "exel_writer",
    "text_to_speech",
    'create_text',
    "on_process_message",
    "get_channel_member",
    "is_member_in_channel",

]
