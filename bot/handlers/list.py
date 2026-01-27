import math
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.models.trip import Trip
from config import ADMIN_ID
import logging

router = Router()
logger = logging.getLogger(__name__)


class ListTrips(StatesGroup):
    browsing = State()


@router.message(Command("list"))
async def cmd_list(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return

    await state.clear()
    await show_trips_page(message, state, page=1)


async def show_trips_page(message: types.Message, state: FSMContext, page: int):
    per_page = 5
    total_trips = Trip.count_all()
    total_pages = math.ceil(total_trips / per_page) if total_trips > 0 else 1

    if page < 1:
        page = 1
    elif page > total_pages:
        page = total_pages

    trips = Trip.get_paginated(page, per_page)

    if not trips:
        await message.answer("Сплавов пока нет. Отправь GPX файл для первого сплава!")
        return

    text = f"📋 Ваши сплавы (стр. {page}/{total_pages}):\n\n"

    for trip in trips:
        media_count = len(trip.get_media())
        media_emoji = '📷' * min(media_count, 3) if media_count else ''
        media_emoji += '...' if media_count > 3 else ''
        media_emoji += '🎬' if any(m.media_type == 'video' for m in trip.get_media()) else ''
        
        text += (f"📅 {trip.trip_date}\n"
                 f"   {trip.distance / 1000:.1f} км | {trip.duration // 3600}ч {(trip.duration % 3600) // 60}м\n"
                 f"   Скорость: {trip.avg_speed:.1f} км/ч {media_emoji}\n"
                 f"   [ID: {trip.id}]\n\n")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton(text="◀", callback_data=f"trip_page_{page-1}"))
    
    nav_buttons.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data=f"trip_page_{page}"))
    
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton(text="▶", callback_data=f"trip_page_{page+1}"))
    
    keyboard.inline_keyboard.append(nav_buttons)

    await state.update_data(current_page=page)

    await message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("trip_page_"))
async def trip_page_callback(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return

    page = int(callback.data.split("_")[2])
    await callback.message.delete()
    await show_trips_page(callback.message, state, page)
    await callback.answer()


@router.callback_query(F.data.startswith("trip_view_"))
async def trip_view_callback(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return

    trip_id = int(callback.data.split("_")[2])
    trip = Trip.get_by_id(trip_id)
    
    if trip:
        from bot.handlers.view import show_trip_details
        await show_trip_details(callback.message, trip, from_list=True)
    
    await callback.answer()
