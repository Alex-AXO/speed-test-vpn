from logger import logger
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import BoundFilter
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import API_TOKEN, ADMINS


bot = Bot(token=API_TOKEN, parse_mode="HTML")  # Инициализация бота    # , disable_web_page_preview=True
dp = Dispatcher(bot)
scheduler = AsyncIOScheduler()  # Инициализация модуля расписания

logger.add("logs/debug.log", format="{time} - {level} - {message}", level="DEBUG",
           rotation="5 days")  # Запись лог-файлов


class IsAdminFilter(BoundFilter):
    key = "is_admin"

    def __init__(self, is_admin):
        self.is_admin = is_admin

    async def check(self, message: types.Message):
        return message.from_user.id in ADMINS


# activate filters
dp.filters_factory.bind(IsAdminFilter)
