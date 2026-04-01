import logging
import json
from requests.exceptions import HTTPError
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import config
import lyricsgenius
from utils.parser_4096 import parser_4096
from utils.genius_errors import genius_error_user_message

logger = logging.getLogger(__name__)


async def callback_handler_main(update, context):
	await update.callback_query.answer()
	song_id = update.callback_query.data
	user = update.effective_user
	logger.info("user=%s action=select_song song_id=%s", user.id, song_id)

	try:
		song_result = config.genius.search_song(song_id=song_id)
	except HTTPError as exc:
		logger.warning("user=%s song_id=%s genius_error=%s", user.id, song_id, type(exc).__name__)
		await update.callback_query.edit_message_text(genius_error_user_message(exc))
		await update.callback_query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))
		return

	if type(song_result) is lyricsgenius.types.song.Song:
		lyrics_string_container = json.loads(song_result.to_json())
		lyrics_string = lyrics_string_container["lyrics"]
		song_full_title = "**" + lyrics_string_container["full_title"] + "**"
		final_string = song_full_title + "\n\n" + lyrics_string + "\n\nSupport us by sharing the bot!"
		list_of_4096_characters = parser_4096(final_string)

		logger.info("user=%s song_id=%s lyrics_chunks=%d", user.id, song_id, len(list_of_4096_characters))
		await update.callback_query.delete_message()
		for block in list_of_4096_characters:
			await update.callback_query.message.reply_text(block)

		context.user_data["audio_search_title"] = lyrics_string_container["full_title"]
		context.user_data["genius_song_id"] = int(song_id)
		get_audio_button = InlineKeyboardButton("Get Audio", callback_data="AUDIOCONTENT:YES")
		no_button = InlineKeyboardButton("No", callback_data="AUDIOCONTENT:NO")
		await update.callback_query.message.reply_text(
			"Do you want to get the audio?",
			reply_markup=InlineKeyboardMarkup([[get_audio_button, no_button]]),
		)
	else:
		logger.warning("user=%s song_id=%s no_lyrics_data", user.id, song_id)
		await update.callback_query.edit_message_text("No lyrics data available.")
		await update.callback_query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))