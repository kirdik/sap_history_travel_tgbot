import os
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ContentType
from bot.models.trip import Trip, Media
from config import MEDIA_DIR, ADMIN_ID
import logging

router = Router()
logger = logging.getLogger(__name__)


class EditTrip(StatesGroup):
    viewing_media = State()
    adding_media = State()


@router.callback_query(F.data.startswith("trip_addmedia_"))
async def trip_addmedia_callback(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return

    trip_id = int(callback.data.split("_")[2])
    await state.update_data(editing_trip_id=trip_id)
    await state.set_state(EditTrip.adding_media)
    
    await callback.message.edit_text("📷 Отправь фото или видео для добавления к сплаву:")
    await callback.answer()


@router.message(EditTrip.adding_media, F.content_type.in_([ContentType.PHOTO, ContentType.VIDEO]))
async def handle_add_media(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return

    data = await state.get_data()
    trip_id = data.get('editing_trip_id')
    trip = Trip.get_by_id(trip_id)
    
    if not trip:
        await message.answer("Сплав не найден.")
        await state.clear()
        return

    try:
        if message.photo:
            media_type = 'photo'
            file = await message.bot.get_file(message.photo[-1].file_id)
            ext = '.jpg'
        else:
            media_type = 'video'
            file = await message.bot.get_file(message.video.file_id)
            ext = '.mp4'

        file_name = f"trip_{trip.id}_{media_type}_{os.path.basename(file.file_path)}"
        file_path = os.path.join(MEDIA_DIR, file_name)
        await message.bot.download_file(file.file_path, file_path)

        trip.add_media(file_path, media_type)
        
        await state.clear()
        await message.answer(f"✅ Медиа добавлено!")
        
        from bot.handlers.view import show_trip_details
        await show_trip_details(message, trip)

    except Exception as e:
        logger.error(f"Error adding media: {e}")
        await message.answer(f"Ошибка: {e}")
        await state.clear()


@router.callback_query(F.data.startswith("trip_delmedia_"))
async def trip_delmedia_callback(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return

    trip_id = int(callback.data.split("_")[2])
    trip = Trip.get_by_id(trip_id)
    
    if not trip:
        await callback.answer("Сплав не найден.")
        return

    media_list = trip.get_media()
    
    if not media_list:
        await callback.answer("Нет медиа для удаления.")
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    
    for media in media_list:
        emoji = "📷" if media.media_type == "photo" else "🎬"
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text=f"{emoji} {os.path.basename(media.file_path)}", callback_data=f"media_delete_{media.id}")
        ])
    
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="❌ Отмена", callback_data=f"trip_view_{trip_id}")
    ])

    await state.update_data(viewing_trip_id=trip_id)
    await state.set_state(EditTrip.viewing_media)

    await callback.message.edit_text(f"🗑️ Выбери медиа для удаления (сплав #{trip_id}):", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(EditTrip.viewing_media, F.data.startswith("media_delete_"))
async def media_delete_callback(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return

    media_id = int(callback.data.split("_")[2])
    data = await state.get_data()
    trip_id = data.get('viewing_trip_id')
    trip = Trip.get_by_id(trip_id)
    
    if trip:
        trip.remove_media(media_id)
    
    await state.clear()
    
    if trip:
        from bot.handlers.view import show_trip_details
        await show_trip_details(callback.message, trip)
    
    await callback.answer()
