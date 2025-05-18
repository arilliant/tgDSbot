import logging
import asyncio
from aiogram import Bot, Dispatcher
from config.settings import settings
from handlers import commands, messages, buttons

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def main() -> None:
    # Проверка конфигурации
    settings.check_config()
    
    # Инициализация бота
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()
    
    # Регистрация роутеров
    dp.include_router(commands.router)
    dp.include_router(buttons.router)
    dp.include_router(messages.router)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())