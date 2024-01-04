from dataclasses import dataclass


@dataclass
class User:
    id: int
    user_id: int
    username: str
    full_name: str
    has_access: bool
    role: str
    weight: int
    height: int
    age: int
    sex: str
    activity: str
    goal: str
    daily_calory: str

    def __repr__(self) -> str:
        return f"""<b>Рост</b>:{self.height}
<b>Вес</b>:{self.weight}
<b>Возраст</b>:{self.age}
<b>Пол</b>:{self.sex}
<b>Активность</b>:{self.activity}
<b>Цель</b>:{self.goal}
<b>Дневная норма</b>:{self.daily_calory}
"""


@dataclass
class Settings:
    height: int
    weight: int
    age: int
    sex: str
    activity: str
    goal: str

    def __repr__(self) -> str:
        return f"Рост:{self.height}\nВес:{self.weight}\nВозраст:{self.age}\nПол:{self.sex}\nАктивность:{self.activity}\nЦель:{self.goal} "


@dataclass
class FoodData:
    id: str | int = None
    dish: str = None
    protein: str = None
    calories: str = None
    grams: str = None
    carbs: str = None
    fats: str = None

    def __repr__(self):
        return f"Блюдо:{self.dish}\nБелки:{self.protein}\nКаллории:{self.calories}\n" \
               f"Граммы:{self.grams}\nУглеводы:{self.carbs}\nЖиры:{self.fats}"
