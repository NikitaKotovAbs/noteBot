from aiogram import Router, F
from aiogram.types import Message
import app.keyboard as kb
import sqlite3

router = Router()
conn = sqlite3.connect("Note.db")
cursor = conn.cursor()

@router.message(F.text == "Посмотреть все заметки")
async def view_note(message: Message):
    user_id = message.from_user.id  # Получаем ID текущего пользователя
    cursor.execute("SELECT id, title, description, is_remind, remind_at FROM Note WHERE user_id = ?", (user_id,))
    notes = cursor.fetchall()

    if notes:
        for note in notes:
            note_id, title, description, is_remind, remind_at = note
            remind_text = f"Напоминание: {'да' if is_remind else 'нет'}"
            remind_at_text = f"Время напоминания: {remind_at}" if remind_at else "Время напоминания не установлено"
            note_text = f"📌 Название: {title}\nОписание: {description}\n{remind_text}\n{remind_at_text}"
            await message.answer(note_text, reply_markup=kb.get_note_inline_keyboard(note_id))
    else:
        await message.answer("У вас пока нет заметок.", reply_markup=kb.keyboard_reply)
