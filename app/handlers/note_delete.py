from aiogram import Router, types
import sqlite3

router = Router()
conn = sqlite3.connect("Note.db")
cursor = conn.cursor()

@router.callback_query(lambda callback: callback.data.startswith("delete_note:"))
async def delete_note_callback(callback: types.CallbackQuery):
    note_id = int(callback.data.split(":")[1])
    cursor.execute("DELETE FROM Note WHERE id = ?", (note_id,))
    conn.commit()
    await callback.message.edit_text("Заметка удалена.")
    await callback.answer("Заметка успешно удалена.", show_alert=True)
