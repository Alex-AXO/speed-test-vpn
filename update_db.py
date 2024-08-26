# poetry shell
# poetry run python ./update_db.py

import sqlite3
from config import DB_PATH


def db_func():

    print('Start db_func')

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Выполнение запроса

    # cursor.execute("""INSERT INTO server_keys (server_name, key) VALUES ('localhost');""")
    # cursor.execute('UPDATE server_keys SET server_name = "axo-outline-12" WHERE server_name = "axo-outline-12pq";')

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
    print("Hi!")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    sql_queries = [
        # '''
        # UPDATE server_keys
        #     SET key = "ss://Y2hhY2hhMjAtaWV0Zi1wb2x5MTMwNTpZWW5lZmpQVEhMUjFjckxSSFNFcVhU@147.45.133.24:20659/?outline=1"
        #     WHERE server_name = "axo-034.tw.nl"
        # '''
        'UPDATE server_keys SET key = REPLACE(key, "176.124.202.194", "91.201.114.89")',
        'UPDATE key_dates SET key = REPLACE(key, "176.124.210.31", "88.210.12.48")',
    ]


    for sql_query in sql_queries:
        cursor.execute(sql_query)

    conn.commit()

    conn.close()
    print('BD updated')


if __name__ == '__main__':
    main()
    # db_create()
    # db_func()
