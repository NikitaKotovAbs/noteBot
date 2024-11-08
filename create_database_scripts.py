import sqlite3

# Подключение к базе данных
conn = sqlite3.connect('Note.db')
cursor = conn.cursor()

# Создание таблицы `access_codes` (если её нет)
cursor.execute('''
CREATE TABLE IF NOT EXISTS Note (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    is_remind boolean NOT NULL DEFAULT FALSE,
    remind_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

''')


cursor.execute('''
CREATE TABLE IF NOT EXISTS Key (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    key TEXT NOT NULL,
    status TEXT CHECK(status IN ('active', 'inactive')) NOT NULL
)

''')


conn.commit()
conn.close()
