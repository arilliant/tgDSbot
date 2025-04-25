from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from keyboards.builders import get_main_keyboard

router = Router()

@router.message(Command("start"))
async def start_command(message: Message) -> None:
    await message.answer(
        "🤖 Привет! Я AI-ассистент.\n\n"
        "Просто напиши мне сообщение, и я постараюсь помочь!\n\n"
        "Используй кнопку ниже или команду /clear чтобы очистить контекст разговора",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )

@router.message(Command("clear"))
async def clear_command(message: Message) -> None:
    from services.context import dialog_context
    dialog_context.clear_context(message.chat.id)
    await message.answer("🔄 Контекст разговора сброшен", reply_markup=get_main_keyboard())