import datetime

import aiosqlite
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import Message
import sqlite3
import app.keyboard as kb

# Инициализация базы данных и планировщика
conn = sqlite3.connect("Note.db")
cursor = conn.cursor()

scheduler = AsyncIOScheduler()

# Функция отправки напоминания
async def send_reminder(bot: Bot, user_id: int, note_id: int, title: str, description: str):
    """Отправка напоминания пользователю."""
    if user_id is None:
        print(f"Ошибка: user_id для заметки {note_id} не найден.")
        return

    try:
        # Получаем обновленную клавиатуру с учетом состояния напоминания
        keyboard = kb.get_note_inline_keyboard(note_id)

        await bot.send_message(
            user_id,
            f"Напоминание о заметке:\n\n"
            f"Заголовок: {title}\n"
            f"Описание: {description}",
            reply_markup=keyboard
        )
    except Exception as e:
        print(f"Ошибка при отправке напоминания для заметки {note_id}: {e}")


# Функция проверки напоминаний
async def check_reminders(bot: Bot):
    """Проверка напоминаний для пользователей и отправка уведомлений."""
    conn = sqlite3.connect("Note.db")
    cursor = conn.cursor()

    # Извлечение напоминаний с правильными столбцами
    cursor.execute("SELECT id, user_id, title, description, remind_at FROM Note WHERE remind_at <= ? AND is_remind = 1",
                   (datetime.datetime.now(),))
    reminders = cursor.fetchall()

    for reminder in reminders:
        note_id, user_id, title, description, remind_at = reminder

        if user_id is None:
            print(f"Ошибка: user_id для заметки {note_id} не найден.")
            continue

        try:
            await send_reminder(bot, user_id, note_id, title, description)
        except Exception as e:
            print(f"Ошибка при отправке напоминания для заметки {note_id}: {e}")


# Функция для остановки напоминания
async def stop_remind(note_id: int):
    """Останавливает напоминания для указанной заметки."""
    conn = sqlite3.connect("Note.db")
    cursor = conn.cursor()

    # Устанавливаем NULL в поле remind_at, чтобы остановить напоминание
    cursor.execute("UPDATE Note SET remind_at = NULL, is_remind = 0 WHERE id = ?", (note_id,))
    conn.commit()

    conn.close()


# Запуск планировщика
async def start_scheduler(bot: Bot):
    """Запуск планировщика."""
    # Задача будет выполняться каждую минуту
    scheduler.add_job(check_reminders, 'interval', minutes=1, args=[bot])  # передаем bot как аргумент
    scheduler.start()

