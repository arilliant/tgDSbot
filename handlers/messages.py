from aiogram import Router
from aiogram.types import Message
from services.openrouter import OpenRouterService

router = Router()

@router.message()
async def handle_message(message: Message) -> None:
    if not message.text or message.text.startswith('/'):
        return
    
    try:
        await message.bot.send_chat_action(message.chat.id, "typing")
        await OpenRouterService.chat_stream(message.text, message, message.bot)
    except Exception as e:
        from config.settings import logger
        logger.error(f"Error processing message: {e}", exc_info=True)
        await message.answer("⚠️ Произошла ошибка при обработке запроса", parse_mode="Markdown")