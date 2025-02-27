from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import config

async def handle_message(update, context):
	user_search=update.message.text
	best_results=[]
	response=config.genius.search_songs(user_search, per_page=5)
	if response:		 #	response["hits"]["result"]["full_title"]:		#checks if we have valid results returned
		for song_object in response["hits"]:
			title_and_songid=[ song_object["result"]["full_title"], song_object["result"]["id"]]
			best_results.append(title_and_songid)
	if len(best_results)==0:
		await update.message.reply_text("No close matches have been found.\n\nTry again...")
		return None
	list_inline_reply=[]
	for pairs in best_results:
		button=InlineKeyboardButton(pairs[0], callback_data=pairs[1])
		list_inline_reply.append([button])
	reply_markup=InlineKeyboardMarkup(list_inline_reply)
	await update.message.reply_text("Select:", reply_markup=reply_markup)
