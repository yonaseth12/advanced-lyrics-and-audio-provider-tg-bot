import logging

from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from handlers.command_handlers import start_command, lyrics_command
from handlers.message_handlers import handle_message, callback_handler_page
from handlers.callback_handler_audio import callback_handler_audio
from handlers.callback_handler_main import callback_handler_main
import config
from database import init_db

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def post_init(application):
    await init_db()
    logger.info("Bot started — polling for updates")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Unhandled exception while handling update", exc_info=context.error)


if __name__ == "__main__":
    config.validate_env()

    app = (
        Application.builder()
        .token(config.TELEGRAM_BOT_TOKEN)
        .read_timeout(60)
        .post_init(post_init)
        .build()
    )

    app.add_error_handler(error_handler)
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("lyrics", lyrics_command))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(CallbackQueryHandler(callback_handler_audio, pattern="^AUDIOCONTENT:"))
    app.add_handler(CallbackQueryHandler(callback_handler_page, pattern="^PAGE:"))
    app.add_handler(CallbackQueryHandler(callback_handler_main))

    app.run_polling(poll_interval=2)