
async def download_with_pytube(update, file_store, pytubeObject, video_file_title):
    try:
        download_path=pytubeObject.download(output_path=file_store, timeout=120, skip_existing=False)
        print(video_file_title, "is downloaded successfully!")
        return download_path
    except Exception as exc:
        await update.callback_query.message.reply_text("Audio could not be downloaded.")
        print(exc)
        return "Interrupted"