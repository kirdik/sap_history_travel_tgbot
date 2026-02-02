import logging
import os

from aiogram import F, Router, types
from aiogram.types import ContentType

from bot.models.trip import Trip
from config import ADMIN_ID, MEDIA_DIR

router = Router()
logger = logging.getLogger(__name__)


@router.message(F.content_type.in_([ContentType.PHOTO, ContentType.VIDEO]))
async def handle_media(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    last_trip = Trip.get_last()
    if not last_trip:
        await message.answer("Сначала добавь сплав (отправь GPX файл).")
        return

    try:
        if message.photo:
            media_type = "photo"
            file = await message.bot.get_file(message.photo[-1].file_id)
        else:
            media_type = "video"
            file = await message.bot.get_file(message.video.file_id)

        file_name = (
            f"trip_{last_trip.id}_{media_type}{os.path.basename(file.file_path)}"
        )
        file_path = os.path.join(MEDIA_DIR, file_name)
        await message.bot.download_file(file.file_path, file_path)

        last_trip.add_media(file_path, media_type)

        emoji = "📷" if media_type == "photo" else "🎬"
        await message.answer(f"{emoji} Медиа добавлено к последнему сплаву!")

    except Exception as e:
        logger.error(f"Error saving media: {e}")
        await message.answer(f"Ошибка при сохранении медиа: {e}")


@router.callback_query(F.data.startswith("trip_viewmedia_"))
async def view_media_callback(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("У вас нет прав для просмотра медиа.")
        return

    trip_id = int(callback.data.split("_")[2])
    trip = Trip.get_by_id(trip_id)

    if not trip:
        await callback.answer("Сплав не найден.")
        return

    media_list = trip.get_media()
    if not media_list:
        await callback.answer("У этого сплава нет медиа.")
        return

    await callback.answer("Загружаю медиа...")  # Acknowledge immediately

    for media_item in media_list:
        try:
            if media_item.media_type == "photo":
                await callback.message.answer_photo(
                    types.FSInputFile(media_item.file_path)
                )
            elif media_item.media_type == "video":
                await callback.message.answer_video(
                    types.FSInputFile(media_item.file_path)
                )
        except Exception as e:
            logger.error(f"Error sending media {media_item.file_path}: {e}")
            await callback.message.answer(
                f"Ошибка при отправке медиа {media_item.file_path}: {e}"
            )
