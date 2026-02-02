import logging
import os

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.models.trip import Trip
from config import ADMIN_ID, GRAPHICS_DIR

router = Router()
logger = logging.getLogger(__name__)


class DeleteTrip(StatesGroup):
    confirming = State()


@router.callback_query(F.data.startswith("trip_confirmdel_"))
async def trip_confirm_del_callback(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return

    trip_id = int(callback.data.split("_")[2])
    trip = Trip.get_by_id(trip_id)

    if not trip:
        await callback.answer("Сплав не найден.")
        return

    await state.update_data(deleting_trip_id=trip_id)
    await state.set_state(DeleteTrip.confirming)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Да, удалить",
                    callback_data=f"trip_delete_confirm_{trip_id}",
                ),
                InlineKeyboardButton(
                    text="❌ Отмена", callback_data=f"trip_view_{trip_id}"
                ),
            ]
        ]
    )

    await callback.message.delete()  # Удаляем исходное сообщение
    await callback.message.answer(
        f"Удалить сплав от {trip.trip_date}? Это действие необратимо!",
        reply_markup=keyboard,
    )
    await callback.answer()


@router.callback_query(DeleteTrip.confirming, F.data.startswith("trip_delete_confirm_"))
async def trip_delete_callback(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return

    trip_id = int(callback.data.split("_")[3])
    trip = Trip.get_by_id(trip_id)

    if trip:
        trip.delete()

        if trip.gpx_path and os.path.exists(trip.gpx_path):
            os.remove(trip.gpx_path)

        graphic_path = os.path.join(GRAPHICS_DIR, f"trip_{trip.trip_date}.png")
        if os.path.exists(graphic_path):
            os.remove(graphic_path)

        for media in trip.get_media():
            if os.path.exists(media.file_path):
                os.remove(media.file_path)

    await state.clear()

    from bot.handlers.list import cmd_list

    await callback.message.delete()
    await cmd_list(callback.message, state)
    await callback.answer()
