import json
import aiohttp
import logging
import asyncio
from config.settings import settings
from services.context import dialog_context
from utils.helpers import process_content

logger = logging.getLogger(__name__)

class OpenRouterService:
    @staticmethod
    async def chat_stream(prompt: str, message, bot):
        chat_id = message.chat.id
        history = dialog_context.get_dialog_history(chat_id)
        
        # Добавляем системный промт, если его нет в начале истории
        if not history or history[0].get("role") != "system":
            system_prompt = settings.SYSTEM_PROMPT
            history = [{"role": "system", "content": system_prompt}] + history

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

        # Константы для оптимизации стриминга
        MAX_MSG_LENGTH = 4000  # Максимальная длина сообщения в Telegram (с запасом)
        UPDATE_INTERVAL = 2.0  # Интервал обновления сообщения в секундах
        UPDATE_CHUNK_SIZE = 100  # Минимальное количество новых символов для обновления

        full_response = ""
        current_part = 1
        parts = []  # Список для хранения частей длинного ответа
        response_message = await message.answer("⏳ Генерирую ответ...", parse_mode="Markdown")
        last_update_time = asyncio.get_event_loop().time()
        last_update_length = 0
        buffer = ""

        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=90)) as session:
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

                    async for chunk in response.content:
                        chunk_str = chunk.decode('utf-8').strip()
                        if not chunk_str.startswith('data:'):
                            continue

                        try:
                            if chunk_str == "data: [DONE]":
                                break
                                
                            data = json.loads(chunk_str[5:])
                            if "choices" in data and data["choices"]:
                                delta = data["choices"][0].get("delta", {})
                                if "content" in delta:
                                    content = process_content(delta["content"])
                                    buffer += content
                                    full_response += content
                                    
                                    current_time = asyncio.get_event_loop().time()
                                    enough_new_content = len(buffer) - last_update_length >= UPDATE_CHUNK_SIZE
                                    enough_time_passed = current_time - last_update_time >= UPDATE_INTERVAL
                                    
                                    # Проверка длины текущего буфера
                                    if len(buffer) > MAX_MSG_LENGTH:
                                        # Cохраняем текущую часть и начинаем новую
                                        parts.append(buffer)
                                        # Важно проверить не пустой ли буфер перед обновлением
                                        if buffer:
                                            await response_message.edit_text(f"{buffer}\n\nЧасть {current_part}/{current_part}...", parse_mode="Markdown")
                                        
                                        # Отправляем новое сообщение для продолжения ответа
                                        response_message = await message.answer("⏳ Продолжение ответа...", parse_mode="Markdown")
                                        buffer = ""
                                        last_update_length = 0
                                        current_part += 1
                                    
                                    # Обновляем сообщение по расписанию или при достаточном количестве нового контента
                                    if (enough_time_passed or enough_new_content) and buffer:  # Проверяем что буфер не пустой
                                        if current_part > 1:
                                            await response_message.edit_text(f"{buffer}\n\nЧасть {current_part}/{current_part}...", parse_mode="Markdown")
                                        else:
                                            await response_message.edit_text(buffer, parse_mode="Markdown")
                                        last_update_time = current_time
                                        last_update_length = len(buffer)
                                    
                        except json.JSONDecodeError as e:
                            logger.warning(f"JSON decode error: {e}")
                        except Exception as e:
                            logger.error(f"Error processing chunk: {e}", exc_info=True)

                    # Завершающее обновление
                    if buffer:  # Убедимся, что буфер не пустой
                        if current_part > 1:
                            parts.append(buffer)
                            await response_message.edit_text(f"{buffer}\n\nЧасть {current_part}/{current_part}", parse_mode="Markdown")
                        else:
                            await response_message.edit_text(buffer, parse_mode="Markdown")
                    else:
                        # Если буфер пустой, используем запасное сообщение
                        await response_message.edit_text("🤷 Не удалось сгенерировать ответ")

                    # Сохраняем полный ответ в истории диалога только если он не пустой
                    if full_response:
                        dialog_context.add_to_dialog_history(chat_id, "assistant", full_response)
                    
                    return full_response

        except aiohttp.ClientError as e:
            logger.error(f"API connection error: {str(e)}", exc_info=True)
            await response_message.edit_text(f"❌ Ошибка соединения с API: повторите попытку позже")
            return ""
        except asyncio.TimeoutError:
            logger.error("API request timed out", exc_info=True)
            await response_message.edit_text(f"⏱️ Превышено время ожидания ответа: запрос слишком сложный")
            return ""
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            await response_message.edit_text(f"❌ Произошла ошибка при обработке запроса")
            return ""