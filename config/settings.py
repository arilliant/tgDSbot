import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    MODEL = "deepseek/deepseek-r1"
  # MODEL = "deepseek/deepseek-chat-v3-0324:free"
    MAX_HISTORY_LENGTH = 20

    @classmethod
    def check_config(cls):
        if not cls.OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY не указан в .env файле")
        if not cls.BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN не указан в .env файле")

settings = Settings()