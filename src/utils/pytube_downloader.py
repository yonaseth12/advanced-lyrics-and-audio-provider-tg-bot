import logging

logger = logging.getLogger(__name__)


async def download_with_pytube(update, file_store, pytubeObject, video_file_title):
    try:
        download_path = pytubeObject.download(output_path=file_store, timeout=120, skip_existing=False)
        logger.info("Downloaded %r to %s", video_file_title, download_path)
        return download_path
    except Exception as exc:
        logger.error("Download failed for %r: %s", video_file_title, exc)
        await update.callback_query.message.reply_text("Audio could not be downloaded.")
        return "Interrupted"