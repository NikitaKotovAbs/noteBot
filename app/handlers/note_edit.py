import datetime

from aiogram import Router, types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
import app.keyboard as kb
from app.states import NoteStates
import sqlite3
from app.handlers.reminders import stop_remind

router = Router()
conn = sqlite3.connect("Note.db")
cursor = conn.cursor()

@router.callback_query(lambda callback: callback.data.startswith("edit_note:"))
async def edit_note_callback(callback: types.CallbackQuery, state: FSMContext):
    note_id = int(callback.data.split(":")[1])

    # Сохраняем id заметки в FSM
    await state.update_data(note_id=note_id)

    # Запрашиваем новое название
    await callback.message.answer("Введите новое название для заметки:")
    await state.set_state(NoteStates.waiting_for_title)
    await callback.answer()

@router.message(NoteStates.waiting_for_title)
async def process_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Введите новое описание заметки:")
    await state.set_state(NoteStates.waiting_for_description)

@router.message(NoteStates.waiting_for_description)
async def process_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Хотите изменить напоминание? (да/нет)")
    await state.set_state(NoteStates.waiting_for_remind_confirmation)

@router.message(NoteStates.waiting_for_remind_confirmation)
async def process_remind_confirmation(message: Message, state: FSMContext):
    remind_text = message.text.lower()
    if remind_text in ["да", "нет"]:
        is_remind = remind_text == "да"
        await state.update_data(is_remind=is_remind)

        if is_remind:
            await message.answer("Через сколько минут напомнить?")
            await state.set_state(NoteStates.waiting_for_remind_time)
        else:
            # Сохранение измененной заметки
            await update_note_in_db(state, message)
    else:
        await message.answer("Пожалуйста, ответьте 'да' или 'нет'.")

@router.message(NoteStates.waiting_for_remind_time)
async def process_remind_time(message: Message, state: FSMContext):
    try:
        remind_minutes = int(message.text)
        remind_at = datetime.datetime.now() + datetime.timedelta(minutes=remind_minutes)
        await state.update_data(remind_at=remind_at)

        await update_note_in_db(state, message)
    except ValueError:
        await message.answer("Пожалуйста, введите число минут.")

async def update_note_in_db(state: FSMContext, message: Message):
    # Получаем данные из состояния
    data = await state.get_data()

    # Проверяем, есть ли 'note_id' в данных
    if 'note_id' not in data:
        await message.answer("Ошибка: заметка не была выбрана для редактирования.")
        return

    note_id = data["note_id"]
    title = data["title"]
    description = data["description"]
    is_remind = data["is_remind"]
    remind_at = data.get("remind_at", None)

    # Проверка, существует ли заметка с таким ID
    cursor.execute("SELECT * FROM Note WHERE id = ?", (note_id,))
    existing_note = cursor.fetchone()

    if not existing_note:
        await message.answer(f"Заметка с ID {note_id} не найдена.")
        return

    # Обновление заметки в базе данных
    cursor.execute(
        "UPDATE Note SET title = ?, description = ?, is_remind = ?, remind_at = ? WHERE id = ?",
        (title, description, is_remind, remind_at, note_id)
    )
    conn.commit()

    # Сообщение пользователю
    await message.answer("Заметка успешно обновлена!", reply_markup=kb.keyboard_reply)
    await state.clear()

router = Router()

# Обработчик для остановки напоминания
@router.callback_query(lambda callback: callback.data.startswith("stop_remind:"))
async def stop_remind_callback(callback: types.CallbackQuery):
    note_id = int(callback.data.split(":")[1])

    # Останавливаем напоминание для заметки
    await stop_remind(note_id)

    # Удаляем текущее сообщение
    await callback.message.delete()

    # Отправляем подтверждение пользователю
    await callback.message.answer("Напоминания для этой заметки остановлены.")

    # Подтверждаем обработку нажатия
    await callback.answer()

    # Очистка состояния
    await callback.answer()

