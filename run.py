# run.py

import aiogram
import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import message
from app.handlers.middlewares import activation_check
from app.handlers import activate_key
from app.handlers import start, note_create, note_view, note_edit, note_delete, note_create_and_edit
from app.handlers.middlewares.activation_check import ActivationCheckMiddleware
from app.handlers.note_edit import router
from app.handlers.reminders import start_scheduler

from config import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def main():
    # Подключаем промежуточный обработчик для проверки активации
    dp.message.middleware(ActivationCheckMiddleware())

    dp.include_router(start.router)
    dp.include_router(note_view.router)
    dp.include_router(note_create_and_edit.router)
    dp.include_router(note_delete.router)
    dp.include_router(router)

    # Подключаем обработчик команды активации
    dp.include_router(activate_key.router)

    await start_scheduler(bot)

    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)  # Только при debug: on
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Bot off')
