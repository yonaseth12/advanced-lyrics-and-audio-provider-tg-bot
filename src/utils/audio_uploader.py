import logging

logger = logging.getLogger(__name__)


async def upload_audio_to_user(file_path, update):
    logger.info("Uploading audio to user=%s file=%s", update.effective_user.id, file_path)
    return await update.callback_query.message.reply_audio(file_path)