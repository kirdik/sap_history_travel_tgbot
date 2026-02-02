import logging
import os
import traceback

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.types import ContentType

from bot.models.trip import Trip
from bot.services.calculator import calculate_metrics
from bot.services.gpx_parser import parse_gpx
from bot.services.graphics import create_infographic
from config import ADMIN_ID, GRAPHICS_DIR, TRACKS_DIR

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    await message.answer(
        "🚣‍♂️ Привет! Я бот для учёта сплавов на сапборде.\n\n"
        "Команды:\n"
        "/start - это сообщение\n"
        "/list - список всех сплавов\n"
        "/stats [day|week|month|year|all] - статистика\n"
        "/last - последний сплав\n\n"
        "Просто отправь GPX файл, чтобы добавить новый сплав!"
    )


@router.message(F.content_type == ContentType.DOCUMENT)
async def handle_gpx_file(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    document = message.document

    if not document.file_name.lower().endswith(".gpx"):
        await message.answer("Пожалуйста, отправь GPX файл.")
        return

    await message.answer("Обрабатываю GPX файл...")

    try:
        file_path = await save_gpx_file(message)
        gpx_data = parse_gpx(file_path)
        logger.info(f"Parsed GPX data: {gpx_data}")

        metrics = calculate_metrics(gpx_data["points"])
        logger.info(f"Calculated metrics: {metrics}")

        graphic_path = os.path.join(GRAPHICS_DIR, f"trip_{metrics['trip_date']}.png")
        create_infographic(metrics, graphic_path)

        Trip.create(
            trip_date=metrics["trip_date"],
            distance=metrics["distance"],
            duration=metrics["duration"],
            avg_speed=metrics["avg_speed"],
            max_speed=metrics["max_speed"],
            min_elevation=metrics["min_elevation"],
            max_elevation=metrics["max_elevation"],
            elevation_gain=metrics["elevation_gain"],
            gpx_path=file_path,
        )

        caption = (
            f"✅ Сплав добавлен!\n\n"
            f"📊 {metrics['trip_date']} | {metrics['distance'] / 1000:.1f} км\n"
        )

        if (
            metrics.get("avg_speed") is not None
            and metrics.get("max_speed") is not None
        ):
            caption += (
                f"⚡ {metrics['avg_speed']:.1f} км/ч (средняя), "
                f"{metrics['max_speed']:.1f} км/ч (макс)\n"
            )
        else:
            caption += "⚡ Скорость: нет данных\n"

        if (
            metrics.get("min_elevation") is not None
            and metrics.get("max_elevation") is not None
        ):
            caption += (
                f"⛰️ {metrics['min_elevation']:.0f}-{metrics['max_elevation']:.0f} м, "
                f"набор: {metrics['elevation_gain']:.0f} м\n"
            )
        else:
            caption += "⛰️ Высота: нет данных\n"

        caption += (
            f"⏱️ {metrics['duration'] // 3600}ч {(metrics['duration'] % 3600) // 60}м"
        )

        await message.answer_photo(types.FSInputFile(graphic_path), caption=caption)

    except Exception as e:
        logger.error(f"Error processing GPX: {e}\n{traceback.format_exc()}")
        await message.answer(f"Ошибка при обработке GPX файла: {e}")


async def save_gpx_file(message: types.Message) -> str:
    document = message.document
    file = await message.bot.get_file(document.file_id)
    file_path = os.path.join(TRACKS_DIR, document.file_name)
    await message.bot.download_file(file.file_path, file_path)
    return file_path
