from datetime import datetime

from loguru import logger

import base64
import json
import subprocess
import re
import os
import asyncio
import aiohttp

import db.main
from initbot import bot
from config import FILE, PORT, ADMINS, MODE, JSON_FILE, ERROR_PING, ERROR_SPEED


def convert_to_mbits(speed_string):
    value, unit = speed_string.split()
    value = float(value)
    if 'Mbit/s' in unit:
        return value
    elif 'Kbit/s' in unit:
        return value / 1000
    elif 'Gbit/s' in unit:
        return value * 1000
    else:
        raise ValueError(f"Неизвестная единица измерения: {unit}")


@logger.catch
def convert_speed_to_kilobytes(speed: str) -> float:
    """Преобразование скорости скачивания в килобайты"""
    try:
        if speed[-1] == 'k':
            return float(speed[:-1])
        elif speed[-1] == 'M':
            return float(speed[:-1]) * 1024
        elif speed[-1] == 'G':
            return float(speed[:-1]) * 1024 * 1024
        else:
            return float(speed) / 1024
    except Exception as e:
        report = f'Error convert_speed_to_kilobytes(): {e}'
        logger.error(report)


@logger.catch
async def speed_test_cli(key_id, server_name, localhost=0):
    """Замеряем скорость через speedtest-cli"""
    logger.debug(f"{server_name}: speedtest-cli started")

    proxychains = 'proxychains4' if MODE == 2 else 'proxychains'
    command = ['speedtest-cli'] if localhost else [proxychains, 'speedtest-cli']

    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            output = stdout.decode()

            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, command, output, stderr)

            ping_match = re.search(r"(\d+(?:\.\d+)?) ms", output)
            download_match = re.search(r"Download: (\d+\.\d+ .bit/s)", output)
            upload_match = re.search(r"Upload: (\d+\.\d+ .bit/s)", output)

            if not all([ping_match, download_match, upload_match]):
                raise ValueError("Не удалось найти все необходимые значения в выводе speedtest-cli")

            ping = round(float(ping_match.group(1)))
            download_speed = convert_to_mbits(download_match.group(1))
            upload_speed = convert_to_mbits(upload_match.group(1))

            report = (f'speedtest-cli result:\n'
                      f'{ping=} ms,\n'
                      f'{download_speed=} Mbit/s,\n'
                      f'{upload_speed=} Mbit/s')
            logger.debug(report)

            if download_speed < ERROR_SPEED or upload_speed < ERROR_SPEED or ping > ERROR_PING:
                await db.main.add_speedtest_info(key_id, ping, download_speed, upload_speed, 1)
                error_msg = (f'{server_name}: speedtest-cli – speed too slow or ping too high: '
                             f'download_speed={download_speed} or upload_speed={upload_speed} < {ERROR_SPEED} '
                             f'or ping={ping} > {ERROR_PING}')
                logger.warning(error_msg)
                await bot.send_message(ADMINS[0], error_msg)
            else:
                await db.main.add_speedtest_info(key_id, ping, download_speed, upload_speed)

            return  # Успешное выполнение, выходим из функции

        except (subprocess.CalledProcessError, ValueError, IndexError) as error:
            logger.error(f"{server_name}: Attempt {attempt}/{max_attempts} failed: {str(error)}")
            if attempt == max_attempts:
                await db.main.add_speedtest_info(key_id, 0, 0, 0, 1)
                error_msg = f'{server_name}: speedtest-cli failed after {max_attempts} attempts: {str(error)}'
                logger.error(error_msg)
                await bot.send_message(ADMINS[0], error_msg)
            else:
                await asyncio.sleep(5)  # Ждем 5 секунд перед следующей попыткой

        except Exception as error:
            await db.main.add_speedtest_info(key_id, 0, 0, 0, 1)
            error_msg = f'{server_name}: Unexpected error in speedtest-cli: {str(error)}'
            logger.error(error_msg)
            await bot.send_message(ADMINS[0], error_msg)
            logger.error(f'Output: {output}')
            return


@logger.catch
async def download_file(key_id, server_name, localhost=0):
    """Скачиваем файл, замеряя время и скорость"""

    try:
        start_time = datetime.now()

        if localhost:
            request = ['curl', '-O', f'https://1090023-cf48670.tmweb.ru/{FILE}']
        else:
            request = ['curl', '-x', f'socks5h://localhost:{PORT}', '-O', f'https://1090023-cf48670.tmweb.ru/{FILE}']

        result = subprocess.run(request, capture_output=True, text=True)
        end_time = datetime.now()

        # Мы можем получить количество секунд с помощью метода total_seconds()
        seconds = round((end_time - start_time).total_seconds())

        # logger.debug(result.stderr)
        last_row = result.stderr.split('\n')[-2].split()  # Получаем последнюю строку в выводе curl
        logger.debug(last_row)

        average_speed = last_row[-6]  # Извлечение последнего вхождения скорости из строки
        average_speed = convert_speed_to_kilobytes(average_speed)  # Преобразование средней скорости в килобайты

        if localhost:
            command = ' '.join(request[0:2])
            file = request[2]
        else:
            command = ' '.join(request[0:4])
            file = request[4]

        report = f"{server_name} | key №{key_id}:\n" \
                 f"Command: {command} + File \n" \
                 f"File: {file}\n" \
                 f"The operation took {seconds} sec. ({round(seconds / 60, 1)} мин.),\n" \
                 f"The average speed is {round(average_speed / 1024, 2)} MB/s."
        logger.success(report)
        # await bot.send_message(ADMINS[0], report)
        await db.main.add_download_info(key_id, average_speed, seconds)  # Запись в БД результата

    except Exception as e:
        await db.main.add_download_info(key_id, 0, 0, 1)
        report = f'{server_name}: error curl-download: {e}'
        logger.error(report)
        await bot.send_message(ADMINS[0], report)


@logger.catch
async def save_keys_number(server_name, key_id):
    """Сохраняем количество ключей в БД"""

    try:
        count_keys = await db.main.get_server_active_keys(server_name)

        if not count_keys:
            error_text = f"save_keys_number(): server not found: {server_name}"
            await bot.send_message(ADMINS[0], error_text)
            logger.error(error_text)
            return

        if count_keys > 50000:
            await db.main.add_active_keys(key_id, count_keys, 1)
            report = f'{server_name}: save_keys_number: {count_keys=}'
            logger.error(report)
            # await bot.send_message(ADMINS[0], report)
        else:
            logger.debug(f"Add {count_keys=} to db")
            await db.main.add_active_keys(key_id, count_keys)

    except Exception as e:
        await db.main.add_active_keys(key_id, 0, 1)
        report = f'{server_name}: error save_keys_number: {e}'
        logger.error(report)
        await bot.send_message(ADMINS[0], report)


@logger.catch
async def speed_test_key(key, key_id, server_name):
    """Main function for new speedtest-cli and download file (curl)"""
    await asyncio.sleep(2)

    if key:  # Если ключ есть (не localhost), то:
        # Расшифровываем ключ
        key = key[5:]  # Удаляем 'ss://'
        first_part, second_part = key.split('@')  # Разделяем ключ на две части
        decoded_first_part = base64.urlsafe_b64decode(first_part + "==").decode('utf-8')  # Декодируем первую часть
        cipher, password = decoded_first_part.split(':')  # Получаем метод шифрования и пароль
        ip, port = second_part.split(':')  # Получаем IP
        port = port.split('/')[0]  # Получаем port

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

        config_str = json.dumps(config)  # Конвертируем в строку

        with open(JSON_FILE, 'w') as f:
            f.write(config_str)  # Запишем конфигурацию в файл

        await asyncio.sleep(1)
        try:  # Попытка подключения к серверу VPN
            # Запускаем ss-local, указывая путь к временному файлу конфигурации
            ss_local = subprocess.Popen(['ss-local', '-v', '-c', JSON_FILE])
            logger.debug(f'{ss_local=}')

            await asyncio.sleep(4)

            # if MODE != 3:
            #     await download_file(key_id, server_name)  # Функция скачивания файла (для замера скорости и времени)
            #     await asyncio.sleep(2)

            await speed_test_cli(key_id, server_name)  # Функция измерения скорости через speedtest-cli

            if MODE == 1:
                await save_keys_number(server_name, key_id)  # Функция записи количества ключей на сервере

        except KeyboardInterrupt:
            # Когда нажимается Ctrl + C, мы попадаем сюда
            print("Interrupted by user, shutting down.")

        except Exception as e:
            report = f"{server_name}: it is impossible to connect to the server, download the file and receive data. " \
                     f"Error: {e}"
            logger.error(report)
            await bot.send_message(ADMINS[0], report)

        finally:
            # Останавливаем ss-local
            ss_local.terminate()
            logger.debug('ss_local.terminate (finally)')

            try:
                # В конце удаляем временный файл
                os.remove(JSON_FILE)

            except Exception as e:
                logger.error(f'Ошибка удаления файла ({JSON_FILE}): {e}')

            # if MODE != 3:
            #     try:
            #         # В конце удаляем временный файл
            #         os.remove(FILE)
            #
            #     except Exception as e:
            #         logger.error(f'Ошибка удаления файла ({FILE}): {e}')

    else:  # Если ключа нет, то это localhost:
        try:
            await asyncio.sleep(1)

            # if MODE != 3:
            #     await download_file(key_id, server_name,
            #                         localhost=1)  # Функция скачивания файла (замер: скорости/времени)
            #     await asyncio.sleep(1)

            await speed_test_cli(key_id, server_name, localhost=1)  # Функция измерения скорости через speedtest-cli

        except KeyboardInterrupt:
            # Когда нажимается Ctrl + C, мы попадаем сюда
            print("Interrupted by user, shutting down.")

        except Exception as e:
            report = f"{server_name}: it is impossible to connect to the server, download the file and receive data. " \
                     f"Error: {e}"
            logger.error(report)
            await bot.send_message(ADMINS[0], report)


@logger.catch
async def check_server_availability(url: str, timeout: int = 5) -> bool:
    """
    Проверяет доступность VPN-сервера по URL.
    :param url: URL сервера.
    :param timeout: Таймаут в секундах.
    :return: True если соединение с сервером установлено, иначе False.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=timeout, ssl=False) as response:
                # Проверяем только возможность установить соединение
                return True
    except aiohttp.ClientError as e:
        logger.error(f"Connection error to {url}. Error: {type(e).__name__}: {e}")
        return False
    except asyncio.TimeoutError:
        logger.error(f"Timeout error connecting to {url}. Timeout: {timeout}s")
        return False
    except Exception as e:
        logger.error(f"Unexpected error checking {url}. Error type: {type(e).__name__}. Message: {e}")
        return False
