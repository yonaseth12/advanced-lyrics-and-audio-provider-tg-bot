import os
from dotenv import load_dotenv

load_dotenv()

TOKEN_GENIUS = os.getenv("TOKEN_GENIUS")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BOT_USERNAME = os.getenv("BOT_USERNAME")

# Shared State Variable
active_status = False

# Genius API Initialization
import lyricsgenius
genius=lyricsgenius.Genius(access_token=TOKEN_GENIUS, response_format="plain", timeout=12)