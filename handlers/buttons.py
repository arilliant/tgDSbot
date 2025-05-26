from aiogram import Router
from aiogram.types import Message
from keyboards.builders import get_main_keyboard
from services.context import dialog_context

router = Router()

@router.message(lambda message: message.text == "🗑 Очистить контекст")
async def clear_context_button(message: Message) -> None:
    dialog_context.clear_context(message.chat.id)
    await message.answer("🔄 Контекст разговора сброшен", reply_markup=get_main_keyboard(), parse_mode="Markdown")