from .MySql import Database
from config.config import load_config
config = load_config("config/config.json", "config/texts.yml")

db = Database(config)

__all__ = ["Database"]
