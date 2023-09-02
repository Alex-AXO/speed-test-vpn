
import sqlite3

from config import DB_PATH


def db_func():

    print('Start db_func')

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Выполнение запроса
    cursor.execute('UPDATE server_keys SET server_name = "axo-outline-08" WHERE server_name = "axo-outline-08ae";')
    cursor.execute('UPDATE server_keys SET server_name = "axo-outline-09" WHERE server_name = "axo-outline-09pq";')
    cursor.execute('UPDATE server_keys SET server_name = "axo-outline-10" WHERE server_name = "axo-outline-10ae";')
    cursor.execute('UPDATE server_keys SET server_name = "axo-outline-11" WHERE server_name = "axo-outline-11ae";')
    cursor.execute('UPDATE server_keys SET server_name = "axo-outline-12" WHERE server_name = "axo-outline-12pq";')

    conn.commit()

    print('finish')

    # Закрытие соединения с базой данных
    conn.close()


def db_create():

    print('Start db_update()')

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Отключаем foreign keys для упрощения операций с таблицами
        cursor.execute("PRAGMA foreign_keys = off;")

        # Создаём новую структуру для таблицы server_keys
        cursor.execute("""
CREATE TABLE IF NOT EXISTS active_keys (
    id             INTEGER  PRIMARY KEY AUTOINCREMENT
                            NOT NULL,
    date_time      DATETIME DEFAULT (DATETIME('now') ),
    key_id                  REFERENCES server_keys (key_id),
    active_keys           INTEGER,
    error          INTEGER
);""")

        cursor.execute("""
CREATE TABLE IF NOT EXISTS download_files (
    id             INTEGER  PRIMARY KEY AUTOINCREMENT
                            NOT NULL,
    date_time      DATETIME DEFAULT (DATETIME('now') ),
    key_id                  REFERENCES server_keys (key_id), 
    download_speed REAL,
    time           INTEGER,
    error          INTEGER
);""")

        cursor.execute("""
CREATE TABLE IF NOT EXISTS server_keys (
            key_id      INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            server_name TEXT,
            key         TEXT,
            note        TEXT
);""")

        # Добавление строки с server_name = "localhost"
        cursor.execute("""INSERT INTO server_keys (server_name) VALUES ('localhost');""")

        cursor.execute("""
CREATE TABLE IF NOT EXISTS speed_tests (
    id             INTEGER  PRIMARY KEY AUTOINCREMENT
                            NOT NULL,
    date_time      DATETIME DEFAULT (DATETIME('now') ),
    key_id         INTEGER  REFERENCES server_keys (key_id),
    ping           REAL,
    download_speed REAL,
    upload_speed   REAL,
    error          INTEGER
);""")

        # Включаем обратно foreign keys
        cursor.execute("PRAGMA foreign_keys = on;")

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
    print('Start main()')
    # Подключение к базе данных
    # conn = sqlite3.connect(DB_PATH)
    # cursor = conn.cursor()

    # Выполнение запроса на получение всех строк из таблицы server_keys
    # cursor.execute('SELECT key_id, server_name, key FROM server_keys')
    # rows = cursor.fetchall()

    # Вывод всех строк
    # print('key_id | server_name | key')
    # print('-------------------------')
    # for row in rows:
    #     print(row[0], '|', row[1], '|', row[2])

    # Закрытие соединения с базой данных
    # conn.close()


if __name__ == '__main__':
    main()
    # db_func()
    db_create()
