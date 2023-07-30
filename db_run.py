
import sqlite3


def add_new_server():
    # Подключение к базе данных
    conn = sqlite3.connect('speedtest.db')
    cursor = conn.cursor()

    # Значения, которые будут добавлены
    key_id = 15
    server_name = 'localhost'

    # Выполнение запроса на добавление новой строки
    cursor.execute('INSERT INTO server_keys (key_id, server_name) VALUES (?, ?)', (key_id, server_name))
    conn.commit()

    print('Новая строка добавлена!')

    # Закрытие соединения с базой данных
    conn.close()


def main():
    # Подключение к базе данных
    conn = sqlite3.connect('speedtest.db')
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
    # add_new_server()
    # main()
