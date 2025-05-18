from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from keyboards.builders import get_main_keyboard
from config.settings import settings

router = Router()

@router.message(Command("start"))
async def start_command(message: Message) -> None:
    await message.answer(
        "🤖 Привет! Я AI-ассистент,\n"
        f"Я использую модель:\n{settings.MODEL}\n\n"
        "Просто напиши мне сообщение, и я постараюсь помочь!\n\n"
        "Используй кнопку ниже или команду /clear чтобы очистить контекст разговора\n\n"
        f"История контекста - {settings.MAX_HISTORY_LENGTH} сообщений",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )

@router.message(Command("clear"))
async def clear_command(message: Message) -> None:
    from services.context import dialog_context
    dialog_context.clear_context(message.chat.id)
    await message.answer("🔄 Контекст разговора сброшен", reply_markup=get_main_keyboard())