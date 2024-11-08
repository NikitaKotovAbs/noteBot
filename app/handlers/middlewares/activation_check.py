# app/middlewares/activation_check.py
from aiogram import BaseMiddleware
from aiogram.types import Message
import sqlite3


class ActivationCheckMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: dict):
        # Пропускаем проверку активации, если команда /activate_key
        if event.text.startswith("/activate_key"):
            return await handler(event, data)

        user_id = event.from_user.id

        # Проверка статуса активации в БД
        conn = sqlite3.connect("Note.db")
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM Key WHERE user_id = ? AND status = 'active'", (user_id,))
        is_active = cursor.fetchone()
        conn.close()

        # Если ключ не активирован, отправляем сообщение и блокируем доступ к функционалу
        if not is_active:
            await event.answer("Для доступа к функционалу активируйте ключ с помощью команды /activate_key <ваш ключ>")
            return

        # Если ключ активен, продолжаем обработку
        return await handler(event, data)
