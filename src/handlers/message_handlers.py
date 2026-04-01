import logging
from requests.exceptions import HTTPError
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import config
from database import upsert_user, log_search
from utils.genius_errors import genius_error_user_message

logger = logging.getLogger(__name__)

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
	user = update.effective_user

	try:
		response = config.genius.search_songs(query, per_page=RESULTS_PER_PAGE, page=page)
	except HTTPError as exc:
		error_name = type(exc).__name__
		logger.warning("user=%s query=%r page=%d genius_error=%s", user.id, query, page, error_name)
		await log_search(user.id, query, None, "error", error_name)
		text = genius_error_user_message(exc)
		if edit_message:
			await edit_message.edit_text(text)
			await edit_message.edit_reply_markup(reply_markup=None)
		else:
			await update.message.reply_text(text)
		return

	hits = response["hits"] if response else []

	if not hits:
		logger.info("user=%s query=%r page=%d results=0", user.id, query, page)
		await log_search(user.id, query, 0, "no_results")
		text = "No close matches have been found.\n\nTry again..."
		if edit_message:
			await edit_message.edit_text(text)
			await edit_message.edit_reply_markup(reply_markup=None)
		else:
			await update.message.reply_text(text)
		return

	logger.info("user=%s query=%r page=%d results=%d", user.id, query, page, len(hits))
	await log_search(user.id, query, len(hits), "success")

	context.user_data["search_query"] = query
	context.user_data["search_page"] = page
	markup = build_results_keyboard(hits, page)
	label = f"Select (page {page}):" if page > 1 else "Select:"

	if edit_message:
		await edit_message.edit_text(label, reply_markup=markup)
	else:
		await update.message.reply_text(label, reply_markup=markup)


async def handle_message(update, context):
	user = update.effective_user
	logger.info("user=%s chat=%s action=search query=%r", user.id, update.effective_chat.id, update.message.text)
	await upsert_user(user)
	await search_and_reply(update.message.text, 1, update, context)


async def callback_handler_page(update, context):
	"""Handle pagination button presses."""
	await update.callback_query.answer()
	page = int(update.callback_query.data.split(":")[1])
	query = context.user_data.get("search_query", "")
	user = update.effective_user
	logger.info("user=%s action=paginate page=%d", user.id, page)
	if not query:
		await update.callback_query.edit_message_text("Session expired. Please search again.")
		return
	await search_and_reply(query, page, update, context, edit_message=update.callback_query.message)
