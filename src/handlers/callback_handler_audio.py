import logging
import os
import googleapiclient.discovery
import pytubefix as pytube
from telegram.error import BadRequest
import config
from database import get_cached_audio, cache_audio
from utils.audio_uploader import upload_audio_to_user
from utils.file_remover_from_server import remove_file_from_server
from utils.pytube_downloader import download_with_pytube

logger = logging.getLogger(__name__)


async def _try_send_cached(msg, file_id: str) -> bool:
	"""Try sending a cached file_id. Returns True on success."""
	try:
		await msg.reply_audio(audio=file_id)
		return True
	except BadRequest:
		return False


async def callback_handler_audio(update, context):
	await update.callback_query.answer()
	callback_data = update.callback_query.data
	user = update.effective_user
	msg = update.callback_query.message

	if callback_data == "AUDIOCONTENT:NO":
		logger.info("user=%s action=audio_declined", user.id)
		await update.callback_query.delete_message()
		return

	song_title = context.user_data.get("audio_search_title", "")
	genius_song_id = context.user_data.get("genius_song_id")
	if not song_title:
		logger.warning("user=%s action=audio_requested no_title_in_session", user.id)
		await msg.reply_text("Session expired. Please search for the song again.")
		return
	logger.info("user=%s action=audio_requested song_id=%s query=%r", user.id, genius_song_id, song_title)

	# --- Check cache first ---
	if genius_song_id is not None:
		cached_file_id = await get_cached_audio(genius_song_id)
		if cached_file_id:
			logger.info("user=%s song_id=%s cache=hit", user.id, genius_song_id)
			if await _try_send_cached(msg, cached_file_id):
				await update.callback_query.delete_message()
				return
			logger.warning("user=%s song_id=%s cache=stale (file_id invalid), re-downloading", user.id, genius_song_id)

	# --- Normal download flow ---
	try:
		youtube_api = googleapiclient.discovery.build(
			serviceName="youtube", version="v3", developerKey=config.GOOGLE_YOUTUBE_API_KEY,
		)
		yt_search_result = youtube_api.search().list(
			q=song_title, type="video", part="id, snippet", maxResults=12,
		).execute()
	except Exception as exc:
		logger.error("user=%s youtube_search_failed error=%s", user.id, exc)
		await msg.reply_text("Can't access the server currently. Server is at full capacity. Try again later! :(")
		return

	result_list = []
	for item in yt_search_result["items"]:
		if (item["id"]["kind"] == "youtube#video"
				and item["snippet"]["liveBroadcastContent"] == "none"
				and len(result_list) < 4):
			video_id = item["id"]["videoId"]
			result_list.append(f"https://www.youtube.com/watch?v={video_id}")

	if not result_list:
		logger.warning("user=%s query=%r youtube_no_results", user.id, song_title)
		await msg.reply_text("No content has been found. Try a different search.")
		return

	video_url = result_list[0]
	logger.info("user=%s video_url=%s", user.id, video_url)
	pytube_obj = pytube.YouTube(video_url, use_oauth=False, allow_oauth_cache=True)
	video_file_title = pytube_obj.title
	stream = pytube_obj.streams.last()

	file_store = os.path.normpath("file_store/")
	download_result = await download_with_pytube(update, file_store, stream, video_file_title)
	if download_result == "Interrupted":
		return

	download_path = download_result
	basename = os.path.basename(download_path)

	sent_message = await upload_audio_to_user(download_path, update)
	logger.info("user=%s action=audio_sent file=%s", user.id, basename)
	await update.callback_query.delete_message()
	remove_file_from_server(download_path, basename)

	# --- Cache the file_id for future requests ---
	if genius_song_id is not None and sent_message and sent_message.audio:
		await cache_audio(genius_song_id, song_title, sent_message.audio.file_id)
		logger.info("user=%s song_id=%s action=audio_cached", user.id, genius_song_id)