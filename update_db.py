# poetry shell
# python ./update_db.py

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
    #     'UPDATE server_keys SET server_name = "axo-901.tw.ru" WHERE server_name = "axo-outline-rus"',
    #     'UPDATE server_keys SET server_name = "axo-003.vd.nl" WHERE server_name = "axo-outline-03"',
    #     'UPDATE server_keys SET server_name = "axo-004.vd.nl" WHERE server_name = "axo-outline-04"',
    #     'UPDATE server_keys SET server_name = "axo-005.vd.nl" WHERE server_name = "axo-outline-05"',
    #     'UPDATE server_keys SET server_name = "axo-006.vd.nl" WHERE server_name = "axo-outline-06"',
    #     'UPDATE server_keys SET server_name = "axo-007.vd.nl" WHERE server_name = "axo-outline-07"',
    #     'UPDATE server_keys SET server_name = "axo-008.ae.se" WHERE server_name = "axo-outline-08"',
    #     'UPDATE server_keys SET server_name = "axo-009.pq.se" WHERE server_name = "axo-outline-09"',
    #     'UPDATE server_keys SET server_name = "axo-010.ae.de" WHERE server_name = "axo-outline-10"',
    #     'UPDATE server_keys SET server_name = "axo-011.ae.at" WHERE server_name = "axo-outline-11"',
    #     'UPDATE server_keys SET server_name = "axo-012.pq.ch" WHERE server_name = "axo-outline-12"',
    #     'UPDATE server_keys SET server_name = "axo-013.ae.se" WHERE server_name = "axo-outline-13"',
    #     'UPDATE server_keys SET server_name = "axo-014.vd.nl" WHERE server_name = "axo-outline-14"',
    #     'UPDATE server_keys SET server_name = "axo-022.ae.se" WHERE server_name = "axo-301.ae.se"'
        '''
        UPDATE server_keys
            SET key = "ss://Y2hhY2hhMjAtaWV0Zi1wb2x5MTMwNTpZWW5lZmpQVEhMUjFjckxSSFNFcVhU@147.45.133.24:20659/?outline=1"
            WHERE server_name = "axo-034.tw.nl"
        '''
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

    # poetry shell
    # python ./update_db.py