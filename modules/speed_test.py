from datetime import datetime

from loguru import logger

import base64
import json
import subprocess
import re
import os
import time

import db.main
from initbot import bot
from config import FILE, PORT, ADMINS


def convert_speed_to_kilobytes(speed: str) -> float:
    """Преобразование скорости скачивания в килобайты"""
    if speed[-1] == 'k':
        return float(speed[:-1])
    elif speed[-1] == 'M':
        return float(speed[:-1]) * 1024
    elif speed[-1] == 'G':
        return float(speed[:-1]) * 1024 * 1024
    else:
        return float(speed) / 1024


async def download_file(key_id):
    """Скачиваем файл, замеряя время и скорость"""

    try:
        start_time = datetime.now()
        result = subprocess.run(['curl', '-x', f'socks5h://localhost:{PORT}', '-O',
                                 f'http://speedtest.wdc01.softlayer.com/downloads/{FILE}'],
                                capture_output=True, text=True)
        end_time = datetime.now()

        # Мы можем получить количество секунд с помощью метода total_seconds()
        seconds = round((end_time - start_time).total_seconds())
    except Exception as e:
        logger.error(f'Error curl-download: {e}')
        await db.main.add_download_info(key_id, 0, 0, 1)
        await bot.send_message(ADMINS[0], f"Error curl-download: {e}")
        return

    try:
        # print(result.stderr)
        # print(result.stderr.split('\n'))
        last_row = result.stderr.split('\n')[-2].split()  # Получаем последнюю строку в выводе curl
        logger.debug(last_row)

    except Exception as e:
        logger.error(f'Failed to get speed and time from strings. Error: {e}')
        logger.error(f'Строка:\n{result.stderr}')
        await bot.send_message(ADMINS[0], f"Failed to get speed and time from strings. Error: {e}")
        return

    average_speed = last_row[-6]    # Извлечение последнего вхождения скорости из строки

    average_speed = convert_speed_to_kilobytes(average_speed)   # Преобразование средней скорости в килобайты

    logger.success(f"\nОперация заняла {seconds} сек. ({round(seconds / 60, 2)} мин.)\n"
                   f"Средняя скорость – {average_speed}")
    await bot.send_message(ADMINS[0], f"Операция заняла {seconds} сек. ({round(seconds / 60, 2)} мин.)\n"
                                      f"Средняя скорость – {average_speed} k")
    await db.main.add_download_info(key_id, average_speed, seconds)


@logger.catch
async def speed_test_key(key, key_id):

    # Расшифровываем ключ
    key = key[5:]  # Удаляем 'ss://'
    first_part, second_part = key.split('@')    # Разделяем ключ на две части
    decoded_first_part = base64.urlsafe_b64decode(first_part + "==").decode('utf-8')    # Декодируем первую часть
    cipher, password = decoded_first_part.split(':')    # Получаем метод шифрования и пароль
    ip, port = second_part.split(':')  # Получаем IP
    port = port.split('/')[0]   # Получаем port

    logger.debug(f"Decoded server data: {cipher=}, password..., {ip=}, {port=}")

    # Создаем JSON-структуру для создания config-файла для подключения
    config = {
        "server": ip,
        "mode": "tcp_and_udp",
        "server_port": int(port),
        "local_address": "127.0.0.1",
        "local_port": PORT,
        "password": password,
        "timeout": 86400,
        "method": cipher
    }

    config_str = json.dumps(config)     # Конвертируем в строку

    with open('config.json', 'w') as f:
        f.write(config_str)     # Запишем конфигурацию в файл

    try:    # Попытка подключения к серверу VPN
        # Запускаем ss-local, указывая путь к временному файлу
        ss_local = subprocess.Popen(['ss-local', '-v', '-c', 'config.json'])

        time.sleep(4)

        await download_file(key_id)   # Функция скачивания файла (для замера скорости и времени)

        # result = subprocess.run(['proxychains', 'speedtest-cli'],
        #                         capture_output=True, text=True)
        # # logger.debug(result)
        #
        # # Извлечение содержимого stdout
        # output = result.stdout
        #
        # # Разбиение вывода на строки
        # lines = output.split('\n')
        #
        # # Паттерн для скорости загрузки
        # download_pattern = re.compile(r"Download: (\d+\.\d+ .bit/s)")
        # upload_pattern = re.compile(r"Upload: (\d+\.\d+ .bit/s)")
        #
        # download_speed = ""
        # upload_speed = ""
        #
        # # Проход по строкам и поиск скоростей загрузки и выгрузки
        # for line in lines:
        #     download_match = download_pattern.search(line)
        #     if download_match:
        #         download_speed = download_match.group(1)
        #
        #     upload_match = upload_pattern.search(line)
        #     if upload_match:
        #         upload_speed = upload_match.group(1)
        #
        # print("Download speed:", download_speed)
        # print("Upload speed:", upload_speed)

    except Exception as e:
        logger.error(f"It is impossible to connect to the server, download the file and receive data. Error: {e}")
        await bot.send_message(ADMINS[0], f"It is impossible to connect to the server, download the file and receive data. Error:: {e}")
        return

    finally:
        # Останавливаем ss-local
        ss_local.terminate()
        logger.debug('ss_local.terminate')

        try:
            # В конце удаляем временный файл
            os.remove('config.json')
            os.remove(FILE)

        except Exception as e:
            logger.error(f'Ошибка удаления файлов: {e}')

        time.sleep(3)
