from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from handlers.command_handlers import start_command, lyrics_command
from handlers.message_handlers import handle_message
from handlers.callback_handler_audio import callback_handler_audio
from handlers.callback_handler_main import callback_handler_main
import config

if __name__ == "__main__":
    app=Application.builder().token(config.TELEGRAM_BOT_TOKEN).read_timeout(60).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("lyrics", lyrics_command))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(CallbackQueryHandler(callback_handler_audio, pattern="^AUDIOCONTENT:"))
    app.add_handler(CallbackQueryHandler(callback_handler_main))	#Fallback Handler
    
    app.run_polling(poll_interval=2)