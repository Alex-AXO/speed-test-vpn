
import sqlite3

from config import DB_PATH


def db_func():

    print('Start db_func')

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Выполнение запроса
    cursor.execute("UPDATE active_keys SET error = 1 WHERE active_keys > 50000;")

    conn.commit()

    print('finish')

    # Закрытие соединения с базой данных
    conn.close()


def db_update():

    print('Start db_update()')

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Отключаем foreign keys для упрощения операций с таблицами
        cursor.execute("PRAGMA foreign_keys = 0;")

        # Создаём временную таблицу для сохранения данных
        cursor.execute("CREATE TABLE sqlitestudio_temp_table AS SELECT * FROM server_keys;")

        # Удаляем старую таблицу
        cursor.execute("DROP TABLE server_keys;")

        # Создаём новую структуру для таблицы server_keys
        cursor.execute("""
        CREATE TABLE server_keys (
            key_id      INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            server_name TEXT,
            key         TEXT,
            note        TEXT
        );
        """)

        # Переносим данные из временной таблицы в новую структуру
        cursor.execute("""
        INSERT INTO server_keys (key_id, server_name, key)
        SELECT key_id, server_name, key FROM sqlitestudio_temp_table;
        """)

        # Удаляем временную таблицу
        cursor.execute("DROP TABLE sqlitestudio_temp_table;")

        # Включаем обратно foreign keys
        cursor.execute("PRAGMA foreign_keys = 1;")

        # Подтверждаем изменения (если вы используете транзакции)
        conn.commit()

    except sqlite3.Error as error:
        # Если произошла ошибка, откатываем транзакцию
        conn.rollback()
        print(f"An error occurred: {error}")

    print('Finish db_update()')

    # Закрытие соединения с базой данных
    conn.close()


def main():
    # Подключение к базе данных
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Выполнение запроса на получение всех строк из таблицы server_keys
    cursor.execute('SELECT key_id, server_name, key FROM server_keys')
    rows = cursor.fetchall()

    # Вывод всех строк
    print('key_id | server_name | key')
    print('-------------------------')
    for row in rows:
        print(row[0], '|', row[1], '|', row[2])

    # Закрытие соединения с базой данных
    conn.close()


if __name__ == '__main__':
    main()
    db_func()
    # db_update()
