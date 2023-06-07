from datetime import datetime

from loguru import logger

import base64
import json
import subprocess
# import re
import os
import time

from config import FILE


@logger.catch
def speed_test_key(key):
    key = key[5:]  # Удаляем 'ss://'

    # Разделяем ключ на две части
    first_part, second_part = key.split('@')

    # Декодируем первую часть
    decoded_first_part = base64.urlsafe_b64decode(first_part + "==").decode('utf-8')

    cipher, password = decoded_first_part.split(':')

    ip, port = second_part.split(':')  # IP и порт не требуют декодирования
    port = port.split('/')[0]

    # print("Cipher:", cipher)
    # print("Password:", password)
    # print("IP:", ip)
    # print("Port:", port)

    # Создаем JSON-структуру
    config = {
        "server": ip,
        "mode": "tcp_and_udp",
        "server_port": int(port),
        "local_address": "127.0.0.1",
        "local_port": 8024,
        "password": password,
        "timeout": 86400,
        "method": cipher
    }

    # Конвертируем в строку
    config_str = json.dumps(config)

    # Запишем конфигурацию в файл
    with open('config.json', 'w') as f:
        f.write(config_str)

    try:
        # Запускаем ss-local, указывая путь к временному файлу
        ss_local = subprocess.Popen(['ss-local', '-v', '-c', 'config.json'])

        time.sleep(3)

        start_time = datetime.now()
        result = subprocess.run(['curl', '-x', 'socks5h://localhost:8024', '-O',
                                 f'http://speedtest.wdc01.softlayer.com/downloads/{FILE}'],
                                capture_output=True, text=True)
        end_time = datetime.now()

        # Мы можем получить количество секунд с помощью метода total_seconds()
        seconds = round((end_time - start_time).total_seconds())

        try:
            # print(result.stderr)
            # print(result.stderr.split('\n'))
            last_row = result.stderr.split('\n')[-2].split()    # Получаем последнюю строку в выводе curl
            logger.debug(last_row)

        except Exception as e:
            logger.error(f'Не смогли получить замеры из строки. Ошибка: {e}')
            logger.error(f'Строка:\n{result.stderr}')
            return 0

        # Извлечение последнего вхождения скорости из строки
        average_speed = last_row[-6]

        logger.success(f"\nОперация заняла {seconds} сек. ({round(seconds / 60, 2)} мин.)\n"
                       f"Средняя скорость – {average_speed}")

    except Exception as e:
        logger.error(f"Возможно не получилось подключится к серверу и произвести замеры. Ошибка: {e}")

    finally:
        # Останавливаем ss-local
        ss_local.terminate()

        try:
            # В конце удаляем временный файл
            os.remove('config.json')
            os.remove(FILE)

        except Exception as e:
            logger.error(f'Ошибка удаления файлов: {e}')

        time.sleep(3)
