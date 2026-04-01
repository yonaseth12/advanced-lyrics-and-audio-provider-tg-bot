import logging
from database import upsert_user

logger = logging.getLogger(__name__)


async def start_command(update, context):
	user = update.effective_user
	logger.info("user=%s chat=%s action=start", user.id, update.effective_chat.id)
	await upsert_user(user)
	await update.message.reply_text("Type to search for lyrics.")


async def lyrics_command(update, context):
	user = update.effective_user
	logger.info("user=%s chat=%s action=lyrics_command", user.id, update.effective_chat.id)
	await upsert_user(user)
	await update.message.reply_text("Search by track/artist: ")
