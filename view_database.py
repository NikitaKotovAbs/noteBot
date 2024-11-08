import sqlite3


def get_all_codes():
    conn = sqlite3.connect('Note.db')
    cursor = conn.cursor()

    # Извлекаем все записи из таблиц access_codes и coupons
    cursor.execute('''
    SELECT Key.id, Key.user_id, Key.status, Key.key
    FROM Key
    ''')
    rows = cursor.fetchall()

    conn.close()
    return rows

# Пример использования
codes = get_all_codes()
for code in codes:
    print(f"ID: {code[0]}, user_id: {code[1]}, Status: {code[2]}, key: {code[3]}")