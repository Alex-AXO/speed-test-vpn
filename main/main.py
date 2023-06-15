from loguru import logger
from aiogram.utils import executor

import handlers.keyboard
from config import ADMINS
import modules
from initbot import scheduler, bot, dp


@logger.catch
async def setup_scheduler(_):
    # scheduler.add_job(modules.schedules.speed_tests, "interval", seconds=5000)
    scheduler.add_job(modules.schedules.speed_tests, "cron", hour=0, minute=11,
                      timezone="Europe/Moscow")  # Свободные слоты для ключей
    scheduler.add_job(modules.schedules.speed_tests, "cron", hour=5, minute=11,
                      timezone="Europe/Moscow")  # Свободные слоты для ключей
    scheduler.add_job(modules.schedules.speed_tests, "cron", hour=10, minute=11,
                      timezone="Europe/Moscow")  # Свободные слоты для ключей
    scheduler.add_job(modules.schedules.speed_tests, "cron", hour=15, minute=11,
                      timezone="Europe/Moscow")  # Свободные слоты для ключей
    scheduler.add_job(modules.schedules.speed_tests, "cron", hour=20, minute=11,
                      timezone="Europe/Moscow")  # Свободные слоты для ключей
    scheduler.start()


@logger.catch
async def on_startup(_):
    await bot.send_message(ADMINS[0], "Speed-Test.VPN.AXO is running!", reply_markup=handlers.keyboard.main)
    logger.success(f"Start speed-test")
    await setup_scheduler(dp)


@logger.catch
async def on_shutdown(_):
    logger.debug("Shutting down..")
    logger.debug("Stop speed-test")


@logger.catch
def main():
    import handlers
    executor.start_polling(dp, skip_updates=False, on_startup=on_startup, on_shutdown=on_shutdown)


if __name__ == '__main__':
    main()
