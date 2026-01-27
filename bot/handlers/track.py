import os
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import ContentType
from bot.services.gpx_parser import parse_gpx
from bot.services.calculator import calculate_metrics
from bot.services.graphics import create_infographic
from bot.models.trip import Trip
from config import TRACKS_DIR, GRAPHICS_DIR, ADMIN_ID
import logging

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

    if not document.file_name.lower().endswith('.gpx'):
        await message.answer("Пожалуйста, отправь GPX файл.")
        return

    await message.answer("Обрабатываю GPX файл...")

    try:
        file_path = await save_gpx_file(message)
        gpx_data = parse_gpx(file_path)
        metrics = calculate_metrics(gpx_data['points'])

        graphic_path = os.path.join(GRAPHICS_DIR, f"trip_{metrics['trip_date']}.png")
        create_infographic(metrics, graphic_path)

        trip = Trip.create(
            trip_date=metrics['trip_date'],
            distance=metrics['distance'],
            duration=metrics['duration'],
            avg_speed=metrics['avg_speed'],
            max_speed=metrics['max_speed'],
            min_elevation=metrics['min_elevation'],
            max_elevation=metrics['max_elevation'],
            elevation_gain=metrics['elevation_gain'],
            gpx_path=file_path
        )

        await message.answer_photo(
            types.FSInputFile(graphic_path),
            caption=f"✅ Сплав добавлен!\n\n"
                    f"📊 {metrics['trip_date']} | {metrics['distance'] / 1000:.1f} км\n"
                    f"⚡ {metrics['avg_speed']:.1f} км/ч (средняя), {metrics['max_speed']:.1f} км/ч (макс)\n"
                    f"⛰️ {metrics['min_elevation']:.0f}-{metrics['max_elevation']:.0f} м, набор: {metrics['elevation_gain']:.0f} м\n"
                    f"⏱️ {metrics['duration'] // 3600}ч {(metrics['duration'] % 3600) // 60}м"
        )

    except Exception as e:
        logger.error(f"Error processing GPX: {e}")
        await message.answer(f"Ошибка при обработке GPX файла: {e}")


async def save_gpx_file(message: types.Message) -> str:
    document = message.document
    file = await message.bot.get_file(document.file_id)
    file_path = os.path.join(TRACKS_DIR, document.file_name)
    await message.bot.download_file(file.file_path, file_path)
    return file_path
