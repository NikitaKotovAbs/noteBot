import sqlite3


def add_key(user_id, key, status):
    conn = sqlite3.connect('Note.db')
    cursor = conn.cursor()

    # Добавляем код в таблицу `access_codes`
    cursor.execute('''
    INSERT INTO Key (user_id, key, status) VALUES (?, ?, ?)
    ''', (user_id, key, status))

    conn.commit()
    conn.close()


# Пример использования
add_key(None, '1:lq5wOH8dbltyIv2gtmxucWbF1G2xYC', 'inactive')
add_key(None, '2:910BUt7sLX6wixGx7u3pbZhVJx2zYJ', 'inactive')
add_key(None, '3:KETtWNDF0JnmRiLISpWRE6gbHmVOZD', 'inactive')
add_key(None, '4:N5NYZi3FQWNcWe6PmzoFe9QPqvJse4', 'inactive')
add_key(None, '5:tc9nbP8XY3zPPQAei9m1WpQsrpyAY9', 'inactive')
add_key(None, '6:atlEWTHKSsfSKxXNTXZw8hdCdQ2Jkh', 'inactive')
add_key(None, '7:W1oydU5j45kC3qH9r5Gq9H1JdohcaH', 'inactive')
add_key(None, '8:tdYqPKHFKutKA8eklmGUKRnScCumCp', 'inactive')
add_key(None, '9:AbHpH49uVnIUrXsXJTzpxkMtMWhtDC', 'inactive')
add_key(None, '10:vR4Wq9tmt1nYVUDCG2bgdpNYNwXhei', 'inactive')
