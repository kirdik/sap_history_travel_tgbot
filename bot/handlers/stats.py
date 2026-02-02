from datetime import datetime, timedelta

from aiogram import Router, types
from aiogram.filters import Command

from bot.models.trip import Trip
from config import ADMIN_ID

router = Router()


@router.message(Command("stats"))
async def cmd_stats(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    args = message.text.split()
    period = args[1] if len(args) > 1 else "all"

    now = datetime.now()
    if period == "day":
        start_date = now.date()
        title = "📊 Статистика за сегодня"
    elif period == "week":
        start_date = (now - timedelta(days=7)).date()
        title = "📊 Статистика за неделю"
    elif period == "month":
        start_date = (now - timedelta(days=30)).date()
        title = "📊 Статистика за месяц"
    elif period == "year":
        start_date = (now - timedelta(days=365)).date()
        title = "📊 Статистика за год"
    else:
        start_date = datetime.min.date()
        title = "📊 Общая статистика"

    trips = [t for t in Trip.get_all() if t.trip_date >= start_date]

    if not trips:
        text = f"{title}\n\nСплавов за этот период нет."
    else:
        total_distance = sum(t.distance or 0 for t in trips) / 1000
        total_duration = sum(t.duration or 0 for t in trips)

        speeds = [t.avg_speed for t in trips if t.avg_speed is not None]
        avg_speed = (sum(speeds) / len(speeds)) if speeds else 0.0

        max_speeds = [t.max_speed for t in trips if t.max_speed is not None]
        max_speed = max(max_speeds) if max_speeds else 0.0

        text = (
            f"{title}\n\n"
            f"📅 Сплавов: {len(trips)}\n"
            f"📍 Общее расстояние: {total_distance:.1f} км\n"
            f"⏱️ Общее время: {total_duration // 3600}ч "
            f"{(total_duration % 3600) // 60}м\n"
            f"⚡ Средняя скорость: {avg_speed:.1f} км/ч\n"
            f"🚀 Максимальная скорость: {max_speed:.1f} км/ч\n\n"
        )

        for trip in trips:
            text += f"• {trip.trip_date}: {(trip.distance or 0) / 1000:.1f} км\n"

    await message.answer(text)


@router.message(Command("last"))
async def cmd_last(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    trip = Trip.get_last()

    if not trip:
        await message.answer("Сплавов пока нет.")
        return

    from bot.handlers.view import show_trip_details

    await show_trip_details(message, trip)
