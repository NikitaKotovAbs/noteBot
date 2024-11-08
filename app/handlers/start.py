from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
import app.keyboard as kb

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Доброе время суток, вас приветствует бот заметок и напоминалок. Чтобы пользоваться нашим продуктом, активируйте ключ доступа, для того чтобы получить доступ к функционалу, используйте команду /activate_key (ваш ключ)", reply_markup=kb.keyboard_reply)


