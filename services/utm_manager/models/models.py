from dataclasses import dataclass


@dataclass(frozen=True)
class UtmData:
    utm_source: str
    utm_medium: str
    utm_campaign: str
    utm_content: str
