import json
import aiohttp
import logging
from config.settings import settings
from services.context import dialog_context
from utils.helpers import process_content

logger = logging.getLogger(__name__)

class OpenRouterService:
    @staticmethod
    async def chat_stream(prompt: str, message, bot):
        chat_id = message.chat.id
        history = dialog_context.get_dialog_history(chat_id)
        
        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        dialog_context.add_to_dialog_history(chat_id, "user", prompt)
        
        payload = {
            "model": settings.MODEL,
            "messages": history + [{"role": "user", "content": prompt}],
            "stream": True
        }

        full_response = []
        response_message = await message.answer("⏳ Генерирую ответ...")
        last_update_length = 0

        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
                async with session.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"API error: {response.status} - {error_text}")
                        await response_message.edit_text("⚠️ Ошибка при обращении к API")
                        return ""

                    buffer = ""
                    async for chunk in response.content:
                        chunk_str = chunk.decode('utf-8').strip()
                        if not chunk_str.startswith('data:'):
                            continue

                        try:
                            data = json.loads(chunk_str[5:])
                            if "choices" in data and data["choices"]:
                                delta = data["choices"][0].get("delta", {})
                                if "content" in delta:
                                    content = process_content(delta["content"])
                                    buffer += content
                                    
                                    if len(buffer) - last_update_length >= 20:
                                        await response_message.edit_text(buffer)
                                        last_update_length = len(buffer)
                        except json.JSONDecodeError as e:
                            logger.warning(f"JSON decode error: {e}")

                    if buffer:
                        await response_message.edit_text(buffer)
                        dialog_context.add_to_dialog_history(chat_id, "assistant", buffer)
                    else:
                        await response_message.edit_text("🤷 Не удалось сгенерировать ответ")

                    return buffer

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            await response_message.edit_text(f"❌ Произошла ошибка: {str(e)}")
            return ""