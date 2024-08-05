from abc import ABC, abstractmethod
from typing import Optional
from models.models import UtmData
from storages.base import MemoryStorage


class BaseUtmManager(ABC):
    def __init__(self) -> None:
        self.storage = MemoryStorage()

    @ abstractmethod
    def extract_utm(self, text) -> Optional[UtmData]:
        ...

    @ abstractmethod
    def save_utm_to_storage(self, user_id: str | int, utm_data: UtmData) -> None:
        ...

    @ abstractmethod
    def get_utm_data_by_user_id(self, user_id: str | int) -> Optional[UtmData]:
        ...
