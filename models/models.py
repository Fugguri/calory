from dataclasses import dataclass
import datetime
from typing import List


@dataclass
class User:
    id: int | None = None
    user_id: int = None
    full_name: str = None
    username: str = None
    has_access: bool | None = None
    role: str | None = None
    weight: int | None = None
    height: int | None = None
    age: int | None = None
    sex: str | None = None
    activity: str | None = None
    goal: str | None = None
    daily_calory: str | None = None
    discount: int | None = None
    subscription: datetime.date | None = None
    free_diary_records: int | None = None
    name: str | None = None
    score: int | None = None

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
    name: str | None = None
    height: int | None = None
    weight: int | None = None
    age: int | None = None
    sex: str | None = None
    activity: str | None = None
    goal: str | None = None

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
        return f"Блюдо:{self.dish}\nБелки:{self.protein}\nБаллов:{self.score}\n" \
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
    telegram_id: str | int = None
    dish: str = None
    protein: str = None
    calories: str = None
    grams: str = None
    carbs: str = None
    fats: str = None
    date: datetime.datetime | None = None
    score: int | str = None

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
