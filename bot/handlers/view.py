import os
from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.models.trip import Trip
from config import GRAPHICS_DIR, ADMIN_ID
import logging

router = Router()
logger = logging.getLogger(__name__)


async def show_trip_details(message: types.Message, trip: Trip, from_list: bool = False):
    media = trip.get_media()
    media_info = ""
    if media:
        photo_count = sum(1 for m in media if m.media_type == 'photo')
        video_count = sum(1 for m in media if m.media_type == 'video')
        parts = []
        if photo_count:
            parts.append(f"📷{photo_count}")
        if video_count:
            parts.append(f"🎬{video_count}")
        media_info = " | ".join(parts)
    else:
        media_info = "Нет"

    text = (f"📊 {trip.trip_date} | {trip.distance / 1000:.1f} км | {trip.duration // 3600}ч {(trip.duration % 3600) // 60}м\n"
            f"⚡ {trip.avg_speed:.1f} км/ч (средняя), {trip.max_speed:.1f} км/ч (макс)\n"
            f"⛰️ {trip.min_elevation:.0f}-{trip.max_elevation:.0f} м, набор: {trip.elevation_gain:.0f} м\n\n"
            f"📎 Медиа: {media_info}")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📷 Добавить медиа", callback_data=f"trip_addmedia_{trip.id}"),
            InlineKeyboardButton(text="🗑️ Удалить медиа", callback_data=f"trip_delmedia_{trip.id}")
        ],
        [
            InlineKeyboardButton(text="🔙 В список", callback_data="trip_list"),
            InlineKeyboardButton(text="❌ Удалить сплав", callback_data=f"trip_confirmdel_{trip.id}")
        ]
    ])

    graphic_path = os.path.join(GRAPHICS_DIR, f"trip_{trip.trip_date}.png")
    if os.path.exists(graphic_path):
        await message.answer_photo(
            types.FSInputFile(graphic_path),
            caption=text,
            reply_markup=keyboard
        )
    else:
        await message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data == "trip_list")
async def trip_list_callback(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return

    from bot.handlers.list import cmd_list, ListTrips
    state = callback.message.bot.get("fsm_storage")
    if state:
        await cmd_list(callback.message, state)
    await callback.answer()
