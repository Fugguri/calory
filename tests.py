from utils import extract_food_data, FoodData

text1 = """Блюдо: Паста с грибами и сливочным соусом
Калории: 450 ккал
Грамм: 350 г
Белки: 15 г
Жиры: 20 г
Углеводы: 55 г"""
dish = FoodData(
    id=
    dish="Паста с грибами и сливочным соусом",
    protein="15",
    calories="450",
    grams="350",
    carbs="55",
    fats="20",
)

text2 = """Блюдо: Паста с грибами и сливочным соусом
Калории: 450 
Грамм: 350 
Белки: 15 
Жиры: 20 
Углеводы: 55 """
dish1 = extract_food_data(text1)
assert dish1 == dish, "Ошибка в формировании блюда" + dish1.__repr__() 
dish2 = extract_food_data(text2)
assert dish1 == dish, "Ошибка в формировании блюда" + dish2.__repr__()
