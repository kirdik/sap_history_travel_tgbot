import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

import config
from bot.handlers import delete, edit, media, stats, track, view
from bot.handlers import list as list_handler

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


async def on_startup(bot: Bot):
    await bot.set_webhook(url=config.WEBHOOK_URL)
    logger.info(f"Webhook set to {config.WEBHOOK_URL}")


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
        # Webhook logic
        dp.startup.register(on_startup)

        app = web.Application()
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
        )
        webhook_requests_handler.register(app, path=config.WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)

        # For nginx reverse proxy, listen on a local host
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host="localhost", port=8000)

        logger.info("Starting webhook server on localhost:8000")
        await site.start()
        await asyncio.Event().wait()  # Run forever
    else:
        # Polling logic
        logger.info("Starting polling...")
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
