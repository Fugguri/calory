
import re
from typing import Optional
from models.models import UtmData
from storages.base import MemoryStorage
from services.utm_manager.base import BaseUtmManager


class TelegramUtmManager(BaseUtmManager):
    def __init__(self, storage: MemoryStorage = None) -> None:
        super().__init__()
        if storage:
            self.storage = storage

    def extract_utm(self, text: str) -> Optional[UtmData]:

        # Define individual regex patterns for UTM parameters
        source_pattern = re.compile(r"source-(?P<source>[^_]+)")
        medium_pattern = re.compile(r"medium-(?P<medium>[^_]+)")
        campaign_pattern = re.compile(r"campaign-(?P<campaign>[^_]+)")
        content_pattern = re.compile(r"content-(?P<content>[^_]+)")

        # Extract each parameter using the appropriate pattern
        utm_source = None
        utm_medium = None
        utm_campaign = None
        utm_content = None

        source_match = source_pattern.search(text)
        if source_match:
            utm_source = source_match.group("source")

        medium_match = medium_pattern.search(text)
        if medium_match:
            utm_medium = medium_match.group("medium")

        campaign_match = campaign_pattern.search(text)
        if campaign_match:
            utm_campaign = campaign_match.group("campaign")

        content_match = content_pattern.search(text)
        if content_match:
            utm_content = content_match.group("content")

        # Ensure all parameters are extracted
        # if utm_source and utm_medium and utm_campaign and utm_content:
        return UtmData(
            utm_source=utm_source or '',
            utm_medium=utm_medium or '',
            utm_campaign=utm_campaign or '',
            utm_content=utm_content or '',
        )

    def save_utm_to_storage(self, user_id: str | int, utm_data: UtmData) -> None:
        self.storage.add_utm_to_user(user_id, utm_data)

    def get_utm_data_by_user_id(self, user_id: str | int) -> Optional[UtmData]:
        return self.storage.get_utm_by_user_id(user_id)


# Create an instance of the UTM manager
utm_manager: TelegramUtmManager = TelegramUtmManager()


if __name__ == "__main__":

    # Test with various input URLs
    urls = [
        "https://t.me/SmartMentalbot?start=source-yandex_medium-smart_mental_MK_campaign-context_content-0",
        "https://t.me/SmartMentalbot?start=source-test_medium-oleg_content-12345",
        "https://t.me/SmartMentalbot?start=source-vnutrenniy_client_medium-client.utm_medium_campaign-client.utm_campaign_content-client.utm_content"
    ]

    for url in urls:
        utm = utm_manager.extract_utm(url)
        print(utm)
