async def start_command(update, context):
	await update.message.reply_text("Type to search for lyrics.")

async def lyrics_command(update, context):
	await update.message.reply_text("Search by track/artist: ")
