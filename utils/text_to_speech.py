import httpx
import wget
import requests


def text_to_speech(text, voice_id):
    headers = {"Accept": "application/json", "Content-Type": "application/json",
               "Authorization": "f9f65ea1-4534-41f3-9d8c-e97d97e77823"}
    body = {'voice_id': voice_id, 'text': text, 'format': 'wav'}

    url = "https://api.voice.steos.io/v1/get/tts"

    # if len(text) >= 1000:
    #     raise TooLongResponce

    response = requests.post(url, headers=headers, json=body)

    data = response.json()
    path = wget.download(data["audio_url"], "voice")

    return path
