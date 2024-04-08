import openai
import base64
import requests
from openai import OpenAI
import httpx
from openai import RateLimitError
from openai import OpenAI
from dotenv import dotenv_values
from db import db
from models.models import FoodData, User


class Calculator:

    def __init__(self) -> None:
        self.config = dotenv_values(".env")
        self.proxy = self.config["proxy"]
        self.openai = OpenAI(
            api_key=self.config['openAi'],

            http_client=httpx.Client(
                proxies=self.proxy,
                transport=httpx.HTTPTransport(local_address="0.0.0.0"),
            ),
        )

        self.assistant = self.openai.beta.assistants.create(
            name="Food recognizer",
            instructions="Ты специалист по питанию, нутрициолог, твоя задача по фото определить состав БЖУ и каллориность пищи. Результат выводи в таблицу. Вес определи приблизительно. Не нужно писать вводную фразу, сразу выдавай таблицу.",
            # tools=[{"type": "code_interpreter"}],
            model="gpt-4-1106-preview"
        )

        self.thread = self.openai.beta.threads.create()

    async def send_photo(self, path: str, text=None,):
        promt = db.get_promt()
        with open(path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            response = self.openai.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {"role": "user",
                        "content": [
                            {"type": "text", "text": promt[0]}
                        ]
                     },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": text if text else "Что это?"},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{encoded_image}",
                                    "detail": "high"
                                },
                            },
                        ],
                    }
                ],
                max_tokens=300,
            )

        return response.choices[0].message.content

    async def daily_count(self, path: str):
        messages = [
            {"role": "system", "content":
                "Скажи сколько каллорий нужно.Убери лишний текст. Формат ответа: Количество каллорий - 2100"},
            {"role": "user", "content": path}]
        response = self.openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,)
        return response.choices[0].message.content.strip()

    async def create_educate_answer(self, food_data=FoodData, user=User):
        print(food_data.__repr__())
        print(user.__repr__())
        messages = [
            {"role": "system", "content":
                '''ты профессиональный нутрициолог с хорошим чувством юмора, ты любишь шутить над своими ученицами. Твоя задача в шутливой форме ответить клиентке с рекомендацией по питанию, в ответе используй ее имя, учти что это ваше первое общение. Закончи призывом к действию, нажать кнопку ниже и начать новую себя Обязательно сообщи ей или ему что ты будешь давайть ей советы раз в день и каждую неделю подводить итоги недели и помогать ей двигаться к цели. Данные будут переданы сообщением
                ПРИМЕР ОТВЕТА:Аня, приветствую тебя в нашем замечательном клубе "Шутливые калорийки"! Ты уже отлично стартовала, вложив 750 ккал в свой "кулинарный капитал" с помощью макарон с котлетой. Это было вкусно, не так ли? Но теперь давай приложим немного стратегии к нашему питанию, чтобы твои калории работали на тебя, а не против!
Я, твой личный нутрициолог с острым юмором, буду каждый день присылать тебе советы, как распорядиться твоим калорийным бюджетом в 1850 ккал. И каждую неделю мы будем вместе анализировать, как ты продвигаешься к своей мечте о стройности, празднуя успехи и корректируя курс.
Так что подготовься, Аня, впереди много интересного! Мы будем смеяться, учиться и, конечно же, худеть. Вместе мы сделаем так, чтобы каждая калория считалась и каждый прием пищи приближал тебя к цели.
А теперь давай действовать! Нажми на кнопку ниже и приступим к созданию новой, еще более замечательной версии тебя. Помни, Аня, каждый шаг вперед – это шаг к твоему успеху. Готова начать? Тогда вперед к приключениям в мире здорового питания и идеальной фигуры!'''},
            {"role": "user", "content": food_data.__repr__()+user.__repr__()}]
        response = self.openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,)
        return response.choices[0].message.content.strip()
