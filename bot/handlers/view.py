import logging
import os

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.models.trip import Trip
from config import ADMIN_ID, GRAPHICS_DIR

router = Router()
logger = logging.getLogger(__name__)


async def show_trip_details(
    message: types.Message, trip: Trip, from_list: bool = False
):
    media = trip.get_media()
    media_info = ""
    if media:
        photo_count = sum(1 for m in media if m.media_type == "photo")
        video_count = sum(1 for m in media if m.media_type == "video")
        parts = []
        if photo_count:
            parts.append(f"📷{photo_count}")
        if video_count:
            parts.append(f"🎬{video_count}")
        media_info = " | ".join(parts)
    else:
        media_info = "Нет"

    text_parts = [
        f"📊 {trip.trip_date} | {(trip.distance or 0) / 1000:.1f} км | "
        f"{(trip.duration or 0) // 3600}ч {((trip.duration or 0) % 3600) // 60}м"
    ]

    if trip.avg_speed is not None:
        text_parts.append(
            f"⚡ {trip.avg_speed:.1f} км/ч (средняя), {trip.max_speed:.1f} км/ч (макс)"
        )

    if trip.min_elevation is not None:
        text_parts.append(
            f"⛰️ {trip.min_elevation:.0f}-{trip.max_elevation:.0f} м, "
            f"набор: {trip.elevation_gain:.0f} м"
        )

    text_parts.append(f"\n📎 Медиа: {media_info}")
    text = "\n".join(text_parts)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📷 Добавить медиа", callback_data=f"trip_addmedia_{trip.id}"
                ),
                InlineKeyboardButton(
                    text="🗑️ Удалить медиа", callback_data=f"trip_delmedia_{trip.id}"
                ),
            ],
            [
                InlineKeyboardButton(text="🔙 В список", callback_data="trip_list"),
                InlineKeyboardButton(
                    text="❌ Удалить сплав", callback_data=f"trip_confirmdel_{trip.id}"
                ),
            ],
        ]
    )

    graphic_path = os.path.join(GRAPHICS_DIR, f"trip_{trip.trip_date}.png")
    if os.path.exists(graphic_path):
        await message.answer_photo(
            types.FSInputFile(graphic_path), caption=text, reply_markup=keyboard
        )
    else:
        await message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data == "trip_list")
async def trip_list_callback(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return

    # Local import to prevent circular dependency (list -> view -> list)
    from bot.handlers.list import cmd_list

    await cmd_list(callback.message, state)
    await callback.answer()
