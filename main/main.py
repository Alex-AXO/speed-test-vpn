from loguru import logger
from aiogram.utils import executor

from config import ADMINS
import modules
from initbot import scheduler, bot, dp


@logger.catch
async def setup_scheduler(dp):
    scheduler.add_job(modules.schedules.speed_tests, "interval", seconds=5000)
    scheduler.start()


@logger.catch
async def on_startup(dp):
    await bot.send_message(ADMINS[0], "VPN.AXO.Bot is running!")
    logger.success(f"Start speed-test")
    await setup_scheduler(dp)


@logger.catch
async def on_shutdown(dp):
    logger.debug("Shutting down..")
    logger.debug("Stop speed-test")


@logger.catch
def main():
    import handlers
    executor.start_polling(dp, skip_updates=False, on_startup=on_startup, on_shutdown=on_shutdown)


if __name__ == '__main__':
    main()
