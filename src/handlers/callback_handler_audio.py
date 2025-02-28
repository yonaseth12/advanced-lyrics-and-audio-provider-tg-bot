import googleapiclient.discovery
import pytube
import os
import config
from utils.audio_uploader import upload_audio_to_user
from utils.file_remover_from_server import remove_file_from_server
from utils.pytube_downloader import download_with_pytube


async def callback_handler_audio(update, context):
	await update.callback_query.answer()
	song_title=update.callback_query.data
	if song_title=="AUDIOCONTENT:NO":
		await update.callback_query.delete_message()
		return "User chose no audio content."
	else:
		song_title=song_title.split(" ", maxsplit=1)[1]
		try:
			youtube_api=googleapiclient.discovery.build(serviceName="youtube", version="v3", developerKey=config.GOOGLE_YOUTUBE_API_KEY)
			yt_search_result=youtube_api.search().list(q=song_title, type="video", part="id, snippet", maxResults=12).execute()
		except:
			await update.message.reply_text("Can't access the server currently. Server is at full capacity. Try again later! :(")
			return "Interrupted"		#Return is used to avoid execution of the rest if youtube search fails
		result_list=[]
		for item in yt_search_result["items"]:
			if item["id"]["kind"] == "youtube#video" and item["snippet"]["liveBroadcastContent"] == "none" and len(result_list) < 4:
				videoId=item["id"]["videoId"]
				videoURL=f"https://www.youtube.com/watch?v={videoId}"
				video_title = item["snippet"]["title"]
				result_list.append(videoURL)

		if result_list:					#if result_list is not empty
			video_url=result_list[0]
			pytubeObject = pytube.YouTube(video_url, use_oauth=False, allow_oauth_cache=True)
			video_file_title = pytubeObject.title
			pytubeObject=pytubeObject.streams.last()

			#Downloading
			file_store=os.path.normpath("file_store/")
			download_result = await download_with_pytube(update, file_store, pytubeObject, video_file_title)
			if download_result == "Interrupted":
				return "Interrupted"
			else:
				download_path = download_result

			#Extracting the Basename
			basename=os.path.basename(download_path)

			#Uploading
			await upload_audio_to_user(download_path, update)
			
			print(f"Successfully uploaded to user {update.callback_query.from_user.first_name}")
			#Remove Inline Keyboard after successful update
			await update.callback_query.delete_message()

			#Removing file from Server
			remove_file_from_server(download_path, basename)
			
		else:
			await update.message.reply_text("No content have been found inside our database.")