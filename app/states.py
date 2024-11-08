# states.py
from aiogram.fsm.state import State, StatesGroup


class NoteStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_remind_confirmation = State()
    waiting_for_remind_datetime = State()
    waiting_for_remind_time = State()


class KeyState(StatesGroup):
    waiting_for_key = State()
