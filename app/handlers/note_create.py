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


@router.message(F.text == "Создать заметку")
async def start_note_creation(message: Message, state: FSMContext):
    await message.answer("Введите название заметки:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(NoteStates.waiting_for_title)


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
