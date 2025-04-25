from config.settings import settings

class DialogContext:
    def __init__(self):
        self._context = {}

    def get_dialog_history(self, chat_id: int) -> list:
        return self._context.get(chat_id, [])

    def add_to_dialog_history(self, chat_id: int, role: str, content: str):
        history = self.get_dialog_history(chat_id)
        if len(history) > settings.MAX_HISTORY_LENGTH:
            history.pop(0)
        history.append({"role": role, "content": content})
        self._context[chat_id] = history

    def clear_context(self, chat_id: int):
        self._context.pop(chat_id, None)

dialog_context = DialogContext()