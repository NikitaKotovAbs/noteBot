import datetime
import sqlite3
from aiogram import Router, types, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from app.states import NoteStates
import app.keyboard as kb

router = Router()

conn = sqlite3.connect("Note.db")
cursor = conn.cursor()

# Обработчик для создания и редактирования заметок
@router.message(F.text == "Создать заметку")
async def start_note_creation(message: Message, state: FSMContext):
    await message.answer("Введите название заметки:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(NoteStates.waiting_for_title)

@router.callback_query(lambda callback: callback.data.startswith("edit_note:"))
async def edit_note_callback(callback: types.CallbackQuery, state: FSMContext):
    note_id = int(callback.data.split(":")[1])
    await state.update_data(note_id=note_id)
    await callback.message.answer("Введите новое название для заметки:")
    await state.set_state(NoteStates.waiting_for_title)

# Обработчик названия для заметки (как для создания, так и для редактирования)
@router.message(NoteStates.waiting_for_title)
async def process_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Введите описание заметки:")
    await state.set_state(NoteStates.waiting_for_description)

# Обработчик описания для заметки
@router.message(NoteStates.waiting_for_description)
async def process_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Хотите, чтобы бот напоминал об этой заметке? (да/нет)")
    await state.set_state(NoteStates.waiting_for_remind_confirmation)

# Обработчик подтверждения напоминания
@router.message(NoteStates.waiting_for_remind_confirmation)
async def process_remind_confirmation(message: Message, state: FSMContext):
    remind_text = message.text.lower()
    if remind_text in ["да", "нет"]:
        is_remind = remind_text == "да"
        await state.update_data(is_remind=is_remind)

        if is_remind:
            await message.answer("Введите дату и время для напоминания (например, 12.12.2024 15:30):")
            await state.set_state(NoteStates.waiting_for_remind_datetime)
        else:
            await save_or_update_note_in_db(state, message)  # Сохранение без напоминания
    else:
        await message.answer("Пожалуйста, ответьте 'да' или 'нет'.")

# Обработчик даты и времени для напоминания
@router.message(NoteStates.waiting_for_remind_datetime)
async def process_remind_datetime(message: Message, state: FSMContext):
    try:
        # Преобразуем строку в формат datetime
        remind_datetime = datetime.datetime.strptime(message.text, "%d.%m.%Y %H:%M")
        await state.update_data(remind_at=remind_datetime)

        await save_or_update_note_in_db(state, message)
    except ValueError:
        await message.answer("Неверный формат даты и времени. Пожалуйста, используйте формат 'дд.мм.гггг чч:мм'.")

# Функция для сохранения или обновления заметки
async def save_or_update_note_in_db(state: FSMContext, message: Message):
    data = await state.get_data()
    title = data["title"]
    description = data["description"]
    is_remind = data["is_remind"]
    remind_at = data.get("remind_at", None)
    note_id = data.get("note_id", None)
    user_id = message.from_user.id  # Сохраняем user_id

    if note_id:  # Если есть note_id, это редактирование
        cursor.execute(
            "UPDATE Note SET title = ?, description = ?, is_remind = ?, remind_at = ?, user_id = ? WHERE id = ?",
            (title, description, is_remind, remind_at, user_id, note_id)
        )
        conn.commit()
        await message.answer("Заметка успешно обновлена!", reply_markup=kb.keyboard_reply)
    else:  # Если нет note_id, это создание новой заметки
        # В функции сохранения или обновления заметки (save_or_update_note_in_db)
        cursor.execute(
            "INSERT INTO Note (title, description, is_remind, remind_at, user_id) VALUES (?, ?, ?, ?, ?)",
            (title, description, is_remind, remind_at, user_id)  # user_id должен быть добавлен
        )

        conn.commit()

        # Удаляем текущее сообщение
        await message.delete()
        await message.answer("Заметка успешно сохранена!", reply_markup=kb.keyboard_reply)

    await state.clear()
