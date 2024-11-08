import asyncio
import datetime
import random
import sqlite3
from aiogram import types, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram import Router
from aiogram.filters import CommandStart, Command, CommandObject
from app.states import NoteStates
from aiogram.fsm.context import FSMContext
import app.keyboard as kb

router = Router()

# Подключение к базе данных
conn = sqlite3.connect("Note.db")
cursor = conn.cursor()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "бот запущен", reply_markup=kb.keyboard_reply
    )


@router.message(F.text == "Создать заметку")
async def start_note_creation(message: Message, state: FSMContext):
    await message.answer("Введите название заметки:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(NoteStates.waiting_for_title)


@router.message(F.text == "Посмотреть все заметки")
async def view_note(message: Message, state: FSMContext):
    await message.answer("Все заметки:", reply_markup=ReplyKeyboardRemove())

    cursor.execute("SELECT id, title, description, is_remind, remind_at FROM Note")
    notes = cursor.fetchall()

    # Проверяем, есть ли заметки
    if notes:
        for note in notes:
            note_id, title, description, is_remind, remind_at = note
            remind_text = f"Напоминание: {'да' if is_remind else 'нет'}"
            remind_at_text = f"Время напоминания: {remind_at}" if remind_at else "Время напоминания не установлено"

            note_text = f"📌 Название: {title}\nОписание: {description}\n{remind_text}\n{remind_at_text}"
            # Используем inline-кнопки для каждой заметки
            await message.answer(note_text, reply_markup=kb.get_note_inline_keyboard(note_id))
    else:
        await message.answer("У вас пока нет заметок.", reply_markup=kb.keyboard_reply)

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
    # Получение данных
    data = await state.get_data()
    note_id = data["note_id"]
    title = data["title"]
    description = data["description"]
    is_remind = data["is_remind"]
    remind_at = data.get("remind_at", None)

    # Обновление заметки в базе данных
    cursor.execute(
        "UPDATE Note SET title = ?, description = ?, is_remind = ?, remind_at = ? WHERE id = ?",
        (title, description, is_remind, remind_at, note_id)
    )
    conn.commit()

    # Сообщение пользователю
    await message.answer("Заметка успешно обновлена!", reply_markup=kb.keyboard_reply)
    await state.clear()

@router.callback_query(lambda callback: callback.data.startswith("delete_note:"))
async def delete_note_callback(callback: types.CallbackQuery):
    note_id = int(callback.data.split(":")[1])

    # Удаляем заметку из базы данных
    cursor.execute("DELETE FROM Note WHERE id = ?", (note_id,))
    conn.commit()

    # Уведомляем пользователя и обновляем интерфейс
    await callback.message.edit_text("Заметка удалена.")
    await callback.answer("Заметка успешно удалена.", show_alert=True)


@router.message(NoteStates.waiting_for_title)
async def process_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Введите описание заметки:")
    await state.set_state(NoteStates.waiting_for_description)


@router.message(NoteStates.waiting_for_description)
async def process_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Хотите, чтобы бот напоминал об этой заметке? (да/нет)")
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
            # Сохранение без напоминания
            await save_note_in_db(state, message)
    else:
        await message.answer("Пожалуйста, ответьте 'да' или 'нет'.")


@router.message(NoteStates.waiting_for_remind_time)
async def process_remind_time(message: Message, state: FSMContext):
    try:
        remind_minutes = int(message.text)
        remind_at = datetime.datetime.now() + datetime.timedelta(minutes=remind_minutes)
        await state.update_data(remind_at=remind_at)

        await save_note_in_db(state, message)
    except ValueError:
        await message.answer("Пожалуйста, введите число минут.")


async def save_note_in_db(state: FSMContext, message: Message):
    # Получение данных
    data = await state.get_data()
    title = data["title"]
    description = data["description"]
    is_remind = data["is_remind"]
    remind_at = data.get("remind_at", None)

    # Сохранение заметки в базе данных
    cursor.execute(
        "INSERT INTO Note (title, description, is_remind, remind_at) VALUES (?, ?, ?, ?)",
        (title, description, is_remind, remind_at)
    )
    conn.commit()

    # Завершение FSM и сообщение пользователю
    await message.answer("Заметка успешно сохранена!", reply_markup=kb.keyboard_reply)
    await state.clear()
