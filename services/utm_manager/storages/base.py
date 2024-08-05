from utils.utm_manager.models import UtmData
from typing import Optional


class MemoryStorage:
    def __init__(self):
        self.user_data = {}

    def add_utm_to_user(self, user_id: str | int, utm_data: UtmData) -> None:
        self.user_data[user_id] = utm_data

    def get_utm_by_user_id(self, user_id: str | int) -> Optional[UtmData]:
        return self.user_data.get(user_id)


class DatabaseStorage:

    def __init__(self):
        self.database = None

    def add_utm_to_user(self, user_id: str | int, utm_data: UtmData) -> None:
        self.user_data[user_id] = utm_data

    def get_utm_by_user_id(self, user_id: str | int) -> Optional[UtmData]:
        return self.user_data.get(user_id)
