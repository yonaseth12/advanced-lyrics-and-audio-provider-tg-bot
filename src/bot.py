from telegram.ext import Application
import config

if __name__ == "__main__":
    app=Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
    
    app.run_polling(poll_interval=2)