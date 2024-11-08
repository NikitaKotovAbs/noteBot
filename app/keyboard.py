import sqlite3

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

keyboard_reply = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Создать заметку')],
    [KeyboardButton(text='Посмотреть все заметки')]
],
    resize_keyboard=True,
    input_field_placeholder='Выберите действие в меню.'
)


def get_note_inline_keyboard(note_id: int):
    """Функция для создания inline-кнопок 'Редактировать' и 'Удалить' для каждой заметки."""

    # Получаем данные о заметке из базы данных для определения состояния напоминания
    conn = sqlite3.connect("Note.db")
    cursor = conn.cursor()
    cursor.execute("SELECT is_remind FROM Note WHERE id = ?", (note_id,))
    result = cursor.fetchone()
    conn.close()

    is_remind = result[0] if result else 0

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Редактировать', callback_data=f'edit_note:{note_id}')],
        [InlineKeyboardButton(text='Удалить', callback_data=f'delete_note:{note_id}')],
    ])

    # Если напоминание активно, добавляем кнопку для остановки напоминания
    if is_remind:
        keyboard.inline_keyboard.append(
            [InlineKeyboardButton(text='Остановить напоминание', callback_data=f'stop_remind:{note_id}')])

    return keyboard


def stop_keyboard(note_id: int):
    """Создание инлайн-клавиатуры для заметки с кнопкой для остановки напоминания."""
    keyboard = InlineKeyboardMarkup(row_width=1)

    stop_button = InlineKeyboardButton("Остановить напоминание", callback_data=f"stop_remind:{note_id}")
    keyboard.add(stop_button)

    return keyboard
