import os
from aiogram import Router, types, F
from aiogram.types import ContentType
from bot.models.trip import Trip
from bot.models.media import Media
from config import MEDIA_DIR, ADMIN_ID
import logging

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
            media_type = 'photo'
            file = await message.bot.get_file(message.photo[-1].file_id)
            ext = '.jpg'
        else:
            media_type = 'video'
            file = await message.bot.get_file(message.video.file_id)
            ext = '.mp4'

        file_name = f"trip_{last_trip.id}_{media_type}{os.path.basename(file.file_path)}"
        file_path = os.path.join(MEDIA_DIR, file_name)
        await message.bot.download_file(file.file_path, file_path)

        last_trip.add_media(file_path, media_type)

        emoji = '📷' if media_type == 'photo' else '🎬'
        await message.answer(f"{emoji} Медиа добавлено к последнему сплаву!")

    except Exception as e:
        logger.error(f"Error saving media: {e}")
        await message.answer(f"Ошибка при сохранении медиа: {e}")
