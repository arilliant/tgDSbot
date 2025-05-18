import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
  # MODEL = "google/gemini-2.5-pro-exp-03-25:free" # Надо оплатить от 10 кредитов OpenRouter
  # MODEL = "qwen/qwen2.5-vl-32b-instruct:free"
    MODEL = "deepseek/deepseek-chat-v3-0324:free"
    MAX_HISTORY_LENGTH = 25

    # Загружаем системный промт из файла
    PROMPT_PATH = os.path.join(os.path.dirname(__file__), "prompt.txt")
    try:
        with open(PROMPT_PATH, "r", encoding="utf-8") as f:
            SYSTEM_PROMPT = f.read().strip()
    except Exception:
        SYSTEM_PROMPT = "Ты — дружелюбный ассистент. Всегда отвечай на русском языке."

    @classmethod
    def check_config(cls):
        if not cls.OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY не указан в .env файле")
        if not cls.BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN не указан в .env файле")

settings = Settings()