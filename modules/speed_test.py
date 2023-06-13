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
from config import FILE, PORT, ADMINS, MODE


@logger.catch
def convert_to_mbits(speed_str):
    """Преобразование скорости скачивания в Mbit/s"""
    speed, unit = speed_str.split()

    speed = float(speed)
    if unit.lower() == 'kbit/s':
        speed /= 1000  # convert from Kbit/s to Mbit/s
    elif unit.lower() == 'gbit/s':
        speed *= 1000  # convert from Gbit/s to Mbit/s

    return speed


@logger.catch
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


@logger.catch
async def speed_test_cli(key_id, server_name):
    """Замеряем скорость через speedtest-cli"""
    logger.debug(f"speedtest-cli started")

    try:
        if MODE == 2:
            proxychains = 'proxychains4'
        else:
            proxychains = 'proxychains'
        result = subprocess.run([proxychains, 'speedtest-cli'],
                                capture_output=True, text=True)
        # logger.debug(result)

        # Извлечение содержимого stdout
        output = result.stdout

    except Exception as e:
        report = f'Error proxychains speedtest-cli: {e}'
        logger.error(report)
        await bot.send_message(ADMINS[0], report)
        await db.main.add_speedtest_info(key_id, 0, 0, 0, 1)
        return

    # Ищем в строке:
    ping = re.findall(r"(\d+(?:\.\d+)?) ms", output)[0]
    download_speed = re.findall(r"Download: (\d+\.\d+ .bit/s)", output)[0]
    upload_speed = re.findall(r"Upload: (\d+\.\d+ .bit/s)", output)[0]

    ping = round(float(ping))
    download_speed = convert_to_mbits(download_speed)
    upload_speed = convert_to_mbits(upload_speed)

    report = f'speedtest-cli result: {ping=} ms,\n' \
             f'{download_speed=} Mbit/s,\n' \
             f'{upload_speed=} Mbit/s'
    logger.debug(report)
    await bot.send_message(ADMINS[0], report)
    await db.main.add_speedtest_info(key_id, ping, download_speed, upload_speed)


@logger.catch
async def download_file(key_id, server_name):
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
        report = f'Error curl-download: {e}'
        logger.error(report)
        await db.main.add_download_info(key_id, 0, 0, 1)
        await bot.send_message(ADMINS[0], report)
        return

    try:
        # print(result.stderr)
        # print(result.stderr.split('\n'))
        logger.debug(result)
        last_row = result.stderr.split('\n')[-2].split()  # Получаем последнюю строку в выводе curl
        logger.debug(last_row)

    except Exception as e:
        report = f'Failed to get speed and time from strings. Error: {e}'
        logger.error(report)
        logger.error(f'String:\n{result.stderr}')
        await bot.send_message(ADMINS[0], report)
        return

    try:
        average_speed = last_row[-6]    # Извлечение последнего вхождения скорости из строки
        logger.debug(f'{average_speed=}')
        numbers = float(average_speed[:-1])
        logger.debug(f'{numbers=}')

    except Exception as e:
        logger.error(f"Can't get speed: {e}")
        await db.main.add_download_info(key_id, 0, 0, 1)
        await bot.send_message(ADMINS[0], f"Error curl-download: {e}")
        return

    average_speed = convert_speed_to_kilobytes(average_speed)   # Преобразование средней скорости в килобайты

    report = f"{server_name} | key №{key_id}:\n" \
             f"The operation took {seconds} sec. ({round(seconds / 60, 1)} мин.),\n"\
             f"The average speed is {round(average_speed / 1024, 2)} MB/s."
    logger.success(report)
    await bot.send_message(ADMINS[0], report)
    await db.main.add_download_info(key_id, average_speed, seconds)


@logger.catch
async def speed_test_key(key, key_id, server_name):
    """Main function"""
    time.sleep(2)

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

    time.sleep(1)
    try:    # Попытка подключения к серверу VPN
        # Запускаем ss-local, указывая путь к временному файлу
        ss_local = subprocess.Popen(['ss-local', '-v', '-c', 'config.json'])
        logger.debug(f'{ss_local=}')

        time.sleep(4)

        await download_file(key_id, server_name)   # Функция скачивания файла (для замера скорости и времени)

        time.sleep(2)

        await speed_test_cli(key_id, server_name)  # Функция измерения скорости через speedtest-cli

    except KeyboardInterrupt:
        # Когда нажимается Ctrl + C, мы попадаем сюда
        print("Interrupted by user, shutting down.")
        # if ss_local.poll() is None:  # если процесс еще выполняется
        #     ss_local.terminate()  # остановить его
        #     logger.debug('ss_local.terminate (KeyboardInterrupt)')
        # return

    except Exception as e:
        logger.error(f"It is impossible to connect to the server, download the file and receive data. Error: {e}")
        await bot.send_message(ADMINS[0], f"It is impossible to connect to the server, download the file and receive data. Error:: {e}")

    finally:

        # Останавливаем ss-local
        ss_local.terminate()
        logger.debug('ss_local.terminate (finally)')

        try:
            # В конце удаляем временный файл
            os.remove('config.json')
            os.remove(FILE)

        except Exception as e:
            logger.error(f'Ошибка удаления файлов: {e}')
