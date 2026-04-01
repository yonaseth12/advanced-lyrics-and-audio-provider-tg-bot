from requests.exceptions import HTTPError
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import config
from utils.genius_errors import genius_error_user_message

RESULTS_PER_PAGE = 5


def build_results_keyboard(hits, page):
	"""Build the inline keyboard with song buttons and pagination row."""
	buttons = []
	for song_object in hits:
		title = song_object["result"]["full_title"]
		song_id = song_object["result"]["id"]
		buttons.append([InlineKeyboardButton(title, callback_data=str(song_id))])

	nav_row = []
	if page > 1:
		nav_row.append(InlineKeyboardButton("⬅ Previous", callback_data=f"PAGE:{page - 1}"))
	if len(hits) == RESULTS_PER_PAGE:
		nav_row.append(InlineKeyboardButton("Next ➡", callback_data=f"PAGE:{page + 1}"))
	if nav_row:
		buttons.append(nav_row)

	return InlineKeyboardMarkup(buttons)


async def search_and_reply(query, page, update, context, *, edit_message=None):
	"""Search Genius and send/edit results with pagination."""
	try:
		response = config.genius.search_songs(query, per_page=RESULTS_PER_PAGE, page=page)
	except HTTPError as exc:
		text = genius_error_user_message(exc)
		if edit_message:
			await edit_message.edit_text(text)
			await edit_message.edit_reply_markup(reply_markup=None)
		else:
			await update.message.reply_text(text)
		return
	hits = response["hits"] if response else []

	if not hits:
		text = "No close matches have been found.\n\nTry again..."
		if edit_message:
			await edit_message.edit_text(text)
			await edit_message.edit_reply_markup(reply_markup=None)
		else:
			await update.message.reply_text(text)
		return

	context.user_data["search_query"] = query
	context.user_data["search_page"] = page
	markup = build_results_keyboard(hits, page)
	label = f"Select (page {page}):" if page > 1 else "Select:"

	if edit_message:
		await edit_message.edit_text(label, reply_markup=markup)
	else:
		await update.message.reply_text(label, reply_markup=markup)


async def handle_message(update, context):
	await search_and_reply(update.message.text, 1, update, context)


async def callback_handler_page(update, context):
	"""Handle pagination button presses."""
	await update.callback_query.answer()
	page = int(update.callback_query.data.split(":")[1])
	query = context.user_data.get("search_query", "")
	if not query:
		await update.callback_query.edit_message_text("Session expired. Please search again.")
		return
	await search_and_reply(query, page, update, context, edit_message=update.callback_query.message)
