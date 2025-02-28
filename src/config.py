import os
from dotenv import load_dotenv

load_dotenv()

TOKEN_GENIUS = os.getenv("TOKEN_GENIUS")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BOT_USERNAME = os.getenv("BOT_USERNAME")
GOOGLE_YOUTUBE_API_KEY=os.getenv("GOOGLE_YOUTUBE_API_KEY")
GOOGLE_ACCOUNT=os.getenv("GOOGLE_ACCOUNT")

# Genius API Initialization
import lyricsgenius
genius=lyricsgenius.Genius(access_token=TOKEN_GENIUS, response_format="plain", timeout=12)
