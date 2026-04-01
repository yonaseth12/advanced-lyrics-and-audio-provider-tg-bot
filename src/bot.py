import logging

from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from handlers.command_handlers import start_command, lyrics_command
from handlers.message_handlers import handle_message, callback_handler_page
from handlers.callback_handler_audio import callback_handler_audio
from handlers.callback_handler_main import callback_handler_main
import config

logging.basicConfig(
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Unhandled exception while handling update", exc_info=context.error)


if __name__ == "__main__":
    app=Application.builder().token(config.TELEGRAM_BOT_TOKEN).read_timeout(60).build()
    app.add_error_handler(error_handler)
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("lyrics", lyrics_command))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(CallbackQueryHandler(callback_handler_audio, pattern="^AUDIOCONTENT:"))
    app.add_handler(CallbackQueryHandler(callback_handler_page, pattern="^PAGE:"))
    app.add_handler(CallbackQueryHandler(callback_handler_main))

    app.run_polling(poll_interval=2)