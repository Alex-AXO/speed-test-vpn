from logger import logger

import db.main
import handlers
from initbot import bot
from config import ADMINS

NO_DATA = 'Нет данных'


@logger.catch
async def last_report(days=7):
    """Отчёт по всем серверам за несколько дней"""
    logger.debug(f'last report | {days=}')

    speedtest_info_last = await db.main.get_speedtest_info_last(days)

    # Get date
    if speedtest_info_last and any(speedtest_info_last):
        min_date = (speedtest_info_last[1].split()[0]).split('-')
        max_date = (speedtest_info_last[2].split()[0]).split('-')
        min_date = f'{min_date[2]}.{min_date[1]}'
        max_date = f'{max_date[2]}.{max_date[1]}.{max_date[0]}'

        # Получите avg_count_per_server
        avg_count_per_server = int(speedtest_info_last[3]) if speedtest_info_last else 0

        await bot.send_message(ADMINS[0], f'{days=} | {min_date}–{max_date} | {avg_count_per_server}', reply_markup=handlers.keyboard.main)

        speedtest_errors_last = await db.main.get_speedtest_errors_last(days)

        download_info_last = await db.main.get_download_info_last(days)
        download_errors_last = await db.main.get_download_errors_last(days)

        servers_active_keys = await db.main.get_servers_active_keys(days)

        # Вывод
        await show_data(speedtest_info_last[0], speedtest_errors_last, download_info_last, download_errors_last,
                        servers_active_keys)

    else:
        await bot.send_message(ADMINS[0], NO_DATA)


@logger.catch
async def week_report(week):
    """Отчёт по всем серверам за конкретную неделю"""

    speedtest_info_week = await db.main.get_speedtest_info_week(week)

    if speedtest_info_week and any(speedtest_info_week):
        # Get date
        min_date = (speedtest_info_week[1].split()[0]).split('-')
        max_date = (speedtest_info_week[2].split()[0]).split('-')
        min_date = f'{min_date[2]}.{min_date[1]}'
        max_date = f'{max_date[2]}.{max_date[1]}.{max_date[0]}'
        await bot.send_message(ADMINS[0], f'{week=} | {min_date}–{max_date}')

        speedtest_errors_week = await db.main.get_speedtest_errors_week(week)

        download_info_week = await db.main.get_download_info_week(week)
        download_errors_week = await db.main.get_download_errors_week(week)

        servers_active_keys = await db.main.get_servers_active_keys_week(week)

        # Вывод
        await show_data(speedtest_info_week[0], speedtest_errors_week, download_info_week, download_errors_week,
                        servers_active_keys)

    else:
        await bot.send_message(ADMINS[0], NO_DATA)


@logger.catch
async def month_report(month):
    """Отчёт по всем серверам за конкретный месяц"""

    # Получить данные из обеих функций
    speedtest_info_month = await db.main.get_speedtest_info_month(month)
    speedtest_errors_month = await db.main.get_speedtest_errors_month(month)

    download_info_month = await db.main.get_download_info_month(month)
    download_errors_month = await db.main.get_download_errors_month(month)

    servers_active_keys = await db.main.get_servers_active_keys_month(month)

    # Вывод
    if speedtest_info_month and any(speedtest_info_month):
        await show_data(speedtest_info_month, speedtest_errors_month, download_info_month, download_errors_month,
                        servers_active_keys)
    else:
        await bot.send_message(ADMINS[0], NO_DATA)


@logger.catch
async def show_data(speedtest_info, speedtest_errors, download_info, download_errors, active_keys=None):
    """Вывод информации (статистики о серверах)"""

    # Преобразовать списки кортежей в словари для лёгкого доступа
    speedtest_info_dict = {
        key_id: (server_name, avg_ping, avg_download, avg_upload)
        for key_id, server_name, avg_ping, avg_download, avg_upload in speedtest_info
    }
    speedtest_errors_dict = {key_id: error_count for key_id, error_count in speedtest_errors}

    download_info_dict = {key_id: (avg_speed, avg_time) for key_id, avg_speed, avg_time in download_info}
    download_errors_dict = {key_id: error_count for key_id, error_count in download_errors}

    # Объединить данные в один словарь
    combined_data = {}
    for key_id in set(speedtest_info_dict.keys()).union(speedtest_errors_dict.keys(),
                                                        download_info_dict.keys(),
                                                        download_errors_dict.keys()):
        # Получить средние скорости и времена из двух словарей, возвращаем 0, если не найдено.
        # avg_ping, avg_download, avg_upload = speedtest_info_dict.get(key_id, (0, 0))
        server_name, avg_ping, avg_download, avg_upload = speedtest_info_dict.get(key_id, ("unknown", 0, 0, 0))
        avg_speed_download, avg_time_download = download_info_dict.get(key_id, (0, 0))

        # Получить количество ошибок из двух словарей, возвращаем 0, если не найдено.
        error_count_speedtest = speedtest_errors_dict.get(key_id, 0)
        error_count_download = download_errors_dict.get(key_id, 0)

        # Добавить данные в словарь
        combined_data[key_id] = {
            "avg_ping": avg_ping,
            "avg_download": avg_download,
            "avg_upload": avg_upload,
            "error_count_speedtest": error_count_speedtest,

            "avg_speed_download": avg_speed_download,
            "avg_time_download": avg_time_download,
            "error_count_download": error_count_download
        }

    if active_keys:
        keys_dict = dict(active_keys)

    # Сначала получаем имена серверов асинхронно
    server_names = {}
    for key_id in combined_data:
        server_name = (await db.main.get_server_name(key_id))[0]
        server_names[key_id] = server_name

    # Сортируем combined_data по имени сервера, используя уже полученные имена
    sorted_combined_data = sorted(combined_data.items(), key=lambda x: server_names[x[0]])

    # Теперь выводим отсортированные данные
    messages = []
    current_message = ""

    for key_id, data in sorted_combined_data:
        avg_ping = round(data['avg_ping'])
        avg_download = round(data['avg_download'])
        avg_upload = round(data['avg_upload'])

        avg_speed_download = round(data['avg_speed_download'] / 1024, 1)
        avg_time_download = round(data['avg_time_download'], 1)

        server_name = server_names[key_id]

        active_key_text = ''
        if active_keys:
            active_key = keys_dict.get(key_id)
            try:
                active_key_text = f"| keys: {int(active_key)}"
            except TypeError:
                active_key_text = ''

        log_text = f'''{key_id=} | {server_name} {active_key_text}
    | {avg_ping=} ms | {avg_download=} Mb/s | {avg_upload=} Mb/s | errs: {data['error_count_speedtest']}
    | download speed: {avg_speed_download} MB/s | time: {avg_time_download} sec. | errs: {data['error_count_download']}'''
        logger.debug(log_text)

        report = f'''
{key_id} | {server_name} {active_key_text} | errs: {data['error_count_speedtest']}
⧖ {avg_ping} ms  ↓ <b>{avg_download}</b> Mbps  ↑ <b>{avg_upload}</b> Mbps
.
.
'''

        if len(current_message + report) > 4000:  # Telegram limit is 4096, we use 4000 to be safe
            messages.append(current_message)
            current_message = report
        else:
            current_message += report

    if current_message:
        messages.append(current_message)

    for message in messages:
        await bot.send_message(ADMINS[0], message)
