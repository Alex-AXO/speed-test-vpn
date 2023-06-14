from datetime import datetime

from loguru import logger

import base64
import json
import subprocess
import re
import os
import time

# import gspread

import db.main
from initbot import bot
from config import FILE, PORT, ADMINS, MODE


@logger.catch
async def week_report_1(days=7):
    """Отчёт по всем серверам за неделю / curl - download file"""
    await bot.send_message(ADMINS[0], f'download_file report | {days=}')
    logger.debug(f'download_file report | {days=}')

    # Получить данные из обеих функций
    download_info_week = await db.main.get_download_info_week(days)
    download_errors_week = await db.main.get_download_errors_week(days)

    # Преобразовать списки кортежей в словари для лёгкого доступа
    download_info_week_dict = {key_id: (avg_speed, avg_time) for key_id, avg_speed, avg_time in download_info_week}
    download_errors_week_dict = {key_id: error_count for key_id, error_count in download_errors_week}

    # Объединить данные в один словарь
    combined_data = {}
    for key_id in set(download_info_week_dict.keys()).union(download_errors_week_dict.keys()):
        avg_speed, avg_time = download_info_week_dict.get(key_id, (0, 0))
        error_count = download_errors_week_dict.get(key_id, 0)
        combined_data[key_id] = {
            "avg_speed": avg_speed,
            "avg_time": avg_time,
            "error_count": error_count,
        }

    for key_id, data in combined_data.items():
        avg_speed = round(data['avg_speed'] / 1024, 1)
        avg_time = round(data['avg_time'], 1)
        server_name = (await db.main.get_server_name(key_id))[0]

        log_text = f'''{key_id=} | {server_name}
| download speed: {avg_speed} MB/s | time: {avg_time} sec. | errors: {data['error_count']}'''
        logger.debug(log_text)
        report = f'''
<b>{server_name}</b>  |  errors: {data['error_count']}
{avg_speed} MB/s  |  {avg_time} sec. 
'''
        await bot.send_message(ADMINS[0], report)


@logger.catch
async def week_report_2(days=7):
    """Отчёт по всем серверам за неделю / speedtest-cli"""
    await bot.send_message(ADMINS[0], f'speedtest-cli report | {days=}')
    logger.debug(f'speedtest-cli report | {days=}')

    # Получить данные из обеих функций
    speedtest_info_week = await db.main.get_speedtest_info_week(days)
    speedtest_errors_week = await db.main.get_speedtest_errors_week(days)

    # Преобразовать списки кортежей в словари для лёгкого доступа
    download_info_week_dict = {key_id: (avg_ping, avg_download, avg_upload) for key_id, avg_ping, avg_download, avg_upload in speedtest_info_week}
    download_errors_week_dict = {key_id: error_count for key_id, error_count in speedtest_errors_week}

    # Объединить данные в один словарь
    combined_data = {}
    for key_id in set(download_info_week_dict.keys()).union(download_errors_week_dict.keys()):
        avg_ping, avg_download, avg_upload = download_info_week_dict.get(key_id, (0, 0, 0))
        error_count = download_errors_week_dict.get(key_id, 0)
        combined_data[key_id] = {
            "avg_ping": avg_ping,
            "avg_download": avg_download,
            "avg_upload": avg_upload,
            "error_count": error_count,
        }

    for key_id, data in combined_data.items():
        avg_ping = round(data['avg_ping'])
        avg_download = round(data['avg_download'])
        avg_upload = round(data['avg_upload'])
        server_name = (await db.main.get_server_name(key_id))[0]

        log_text = f'''{key_id=} | {server_name} 
| {avg_ping=} ms | {avg_download=} Mb/s | {avg_upload=} Mb/s | errors: {data['error_count']}'''
        logger.debug(log_text)

        report = f'''
<b>{server_name}</b> | errors: {data['error_count']}
{avg_ping} ms  |  {avg_download} MB/s  |  {avg_upload} Mb/s
'''
        await bot.send_message(ADMINS[0], report)
