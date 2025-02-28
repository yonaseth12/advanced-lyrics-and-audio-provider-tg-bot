async def upload_audio_to_user(file_path, update):
    print("Initiating upload...")
    await update.callback_query.message.reply_audio(file_path)		#Relative path can also be passed:    .reply_audio(os.path.join(file_store, basename))
    print(f"Successfully uploaded to user {update.callback_query.from_user.first_name}")