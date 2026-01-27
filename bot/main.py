import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
import config
from bot.handlers import track, media, list as list_handler, view, edit, delete, stats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Помощь"),
        BotCommand(command="/list", description="Список сплавов"),
        BotCommand(command="/stats", description="Статистика"),
        BotCommand(command="/last", description="Последний сплав"),
    ]
    await bot.set_my_commands(commands)


async def main():
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(track.router)
    dp.include_router(media.router)
    dp.include_router(list_handler.router)
    dp.include_router(view.router)
    dp.include_router(edit.router)
    dp.include_router(delete.router)
    dp.include_router(stats.router)

    await set_bot_commands(bot)

    if config.WEBHOOK_URL:
        await bot.set_webhook(url=config.WEBHOOK_URL)
        logger.info(f"Webhook set to {config.WEBHOOK_URL}")
    else:
        logger.info("Starting polling...")

    try:
        if config.WEBHOOK_URL:
            await dp.start_webhook(bot=bot)
        else:
            await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
