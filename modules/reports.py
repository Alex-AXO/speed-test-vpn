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
async def week_report():
    """Отчёт по всем серверам за неделю"""
    await bot.send_message(ADMINS[0], f'week_report')
    logger.debug('week_report')

    # gc = gspread.service_account(filename='speedtest-vpn-axo-99761f8bc987.json')
    #
    # # sh = gc.create('speedtest-vpn-axo.Report')
    #
    # # Откройте новую таблицу и получите первый лист
    # worksheet = gc.open("speedtest-vpn-axo.Report").sheet1
    # logger.debug(worksheet)
    #
    # # Обновите ячейки
    # worksheet.update('A1', [[1, 2], [3, 4], [5, 6]])
    # logger.debug(worksheet)

