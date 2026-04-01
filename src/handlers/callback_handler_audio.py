import logging
import os
import googleapiclient.discovery
import pytubefix as pytube
import config
from utils.audio_uploader import upload_audio_to_user
from utils.file_remover_from_server import remove_file_from_server
from utils.pytube_downloader import download_with_pytube

logger = logging.getLogger(__name__)


async def callback_handler_audio(update, context):
	await update.callback_query.answer()
	song_title = update.callback_query.data
	user = update.effective_user
	msg = update.callback_query.message

	if song_title == "AUDIOCONTENT:NO":
		logger.info("user=%s action=audio_declined", user.id)
		await update.callback_query.delete_message()
		return

	song_title = context.user_data.get("audio_search_title", "")
	if not song_title:
		logger.warning("user=%s action=audio_requested no_title_in_session", user.id)
		await msg.reply_text("Session expired. Please search for the song again.")
		return
	logger.info("user=%s action=audio_requested query=%r", user.id, song_title)

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

	await upload_audio_to_user(download_path, update)
	logger.info("user=%s action=audio_sent file=%s", user.id, basename)
	await update.callback_query.delete_message()
	remove_file_from_server(download_path, basename)