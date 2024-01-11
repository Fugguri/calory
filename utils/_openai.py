import openai
import base64
import requests
from openai import OpenAI
import httpx
from openai import RateLimitError
from openai import OpenAI
from dotenv import dotenv_values
from db import db


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
