# app/handlers/activate_key.py
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
import app.keyboard as kb
import sqlite3

router = Router()

# Функция активации ключа
@router.message(Command('activate_key'))
async def activate_key(message: Message, command: CommandObject):
    # Получаем аргумент (введенный ключ) после команды
    key_input = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
    user_id = message.from_user.id

    if not key_input:
        await message.answer("Пожалуйста, введите ключ после команды.")
        return

    # Подключение к БД и проверка ключа
    conn = sqlite3.connect("Note.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, status FROM Key WHERE key = ?", (key_input,))
    result = cursor.fetchone()

    if result is None:
        await message.answer("Ключ не найден. Проверьте и попробуйте снова.")
    else:
        key_id, status = result
        if status == "active":
            await message.answer("Этот ключ уже активирован.")
        else:
            # Обновляем статус и сохраняем user_id
            cursor.execute("UPDATE Key SET status = 'active', user_id = ? WHERE id = ?", (user_id, key_id))
            conn.commit()
            await message.answer("Ключ успешно активирован! Теперь вам доступен весь функционал бота.",  reply_markup=kb.keyboard_reply)

    conn.close()
