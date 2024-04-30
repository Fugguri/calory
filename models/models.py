from dataclasses import dataclass
import datetime
from typing import List


@dataclass
class User:
    id: int
    user_id: int
    full_name: str
    username: str
    has_access: bool
    role: str
    weight: int
    height: int
    age: int
    sex: str
    activity: str
    goal: str
    daily_calory: str
    discount: int
    subscription: datetime.date
    free_diary_records: int
    name: str
    score: int

    def __repr__(self) -> str:
        return f"""<b>Имя</b>:{self.name}
<b>Рост</b>:{self.height}
<b>Вес</b>:{self.weight}
<b>Возраст</b>:{self.age}
<b>Пол</b>:{self.sex}
<b>Активность</b>:{self.activity}
<b>Цель</b>:{self.goal}
<b>Дневная норма</b>:{self.daily_calory}
"""


@dataclass
class Settings:
    name: str
    height: int
    weight: int
    age: int
    sex: str
    activity: str
    goal: str

    def __repr__(self) -> str:
        return f"Имя:{self.name}\nРост:{self.height}\nВес:{self.weight}\nВозраст:{self.age}\nПол:{self.sex}\nАктивность:{self.activity}\nЦель:{self.goal} "


@dataclass
class FoodData:
    id: str | int = None
    dish: str = None
    protein: str = None
    calories: str = None
    grams: str = None
    carbs: str = None
    fats: str = None
    score: int = None

    def __repr__(self):
        return f"Блюдо:{self.dish}\nБелки:{self.protein}\nКаллории:{self.calories}\n" \
               f"Граммы:{self.grams}\nУглеводы:{self.carbs}\nЖиры:{self.fats}"


@dataclass
class Promo:
    id: int = None
    code: str = None
    percent: int = None
    amount: int = 0

    def __repr__(self):
        return f"ПРОМОКОД:{self.code}\nПРОЦЕНТЫ: {self.percent}%\nИСПОЛЬЗОВАНО: {self.amount}"


@dataclass
class Record:
    id: str | int = None
    dish: str = None
    protein: str = None
    calories: str = None
    grams: str = None
    carbs: str = None
    fats: str = None
    date: datetime.datetime | None = None

    # def __repr__(self):
    #     return f"ПРОМОКОД:{self.code}\nПРОЦЕНТЫ: {self.percent}%\nИСПОЛЬЗОВАНО: {self.amount}"


@dataclass
class UserWithYesterdayRecords:
    user: User
    records: List[Record]


@dataclass
class UserWithWeeklyRecords:
    user: User
    records: List[Record]
