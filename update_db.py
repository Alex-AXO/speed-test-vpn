
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
    #     'PRAGMA foreign_keys = 0;',
    #     'CREATE TABLE sqlitestudio_temp_table AS SELECT * FROM servers;',
    #     'DROP TABLE servers;',
    #     '''CREATE TABLE servers (
    # server_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    # name          TEXT    NOT NULL
    #                       UNIQUE,
    # api_url       TEXT    NOT NULL
    #                       UNIQUE,
    # server_status INTEGER,
    # max_users     INTEGER,
    # note          TEXT,
    # active_users  INTEGER,
    # country       TEXT,
    # hoster        TEXT,
    # chatgpt       INTEGER);''',
    #     '''INSERT INTO servers (
    #                     server_id,
    #                     name,
    #                     api_url,
    #                     server_status,
    #                     max_users,
    #                     note,
    #                     active_users
    #                 )
    #                 SELECT server_id,
    #                        name,
    #                        api_url,
    #                        server_status,
    #                        max_users,
    #                        note,
    #                        active_users
    #                   FROM sqlitestudio_temp_table;''',
    #     'DROP TABLE sqlitestudio_temp_table;',
    #     'PRAGMA foreign_keys = 1;',
        'UPDATE servers SET name = "axo-901.tw.ru", chatgpt = 0 WHERE name = "axo-outline-rus"',
        'UPDATE servers SET name = "axo-003.vd.nl", chatgpt = 0 WHERE name = "axo-outline-03"',
        'UPDATE servers SET name = "axo-004.vd.nl", chatgpt = 0 WHERE name = "axo-outline-04"',
        'UPDATE servers SET name = "axo-005.vd.nl", chatgpt = 0 WHERE name = "axo-outline-05"',
        'UPDATE servers SET name = "axo-006.vd.nl", chatgpt = 0 WHERE name = "axo-outline-06"',
        'UPDATE servers SET name = "axo-007.vd.nl", chatgpt = 0 WHERE name = "axo-outline-07"',
        'UPDATE servers SET name = "axo-008.ae.se", chatgpt = 1 WHERE name = "axo-outline-08"',
        'UPDATE servers SET name = "axo-009.pq.se", chatgpt = 1 WHERE name = "axo-outline-09"',
        'UPDATE servers SET name = "axo-010.ae.de", chatgpt = 0 WHERE name = "axo-outline-10"',
        'UPDATE servers SET name = "axo-011.ae.at", chatgpt = 0 WHERE name = "axo-outline-11"',
        'UPDATE servers SET name = "axo-012.pq.ch", chatgpt = 1 WHERE name = "axo-outline-12"',
        'UPDATE servers SET name = "axo-013.ae.se", chatgpt = 0 WHERE name = "axo-outline-13"',
        'UPDATE servers SET name = "axo-014.vd.nl", chatgpt = 0 WHERE name = "axo-outline-14"',
        'UPDATE servers SET name = "axo-015.4v.ch", chatgpt = 0 WHERE name = "axo-outline-15"',
        'UPDATE servers SET name = "axo.016.4v.se", chatgpt = 0 WHERE name = "axo-016.4v.se"'
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
