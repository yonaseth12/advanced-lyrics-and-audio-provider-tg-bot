import os
import sys
import logging
from dotenv import load_dotenv
import lyricsgenius

load_dotenv()

logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TOKEN_GENIUS = os.getenv("TOKEN_GENIUS")
GOOGLE_YOUTUBE_API_KEY = os.getenv("GOOGLE_YOUTUBE_API_KEY")
BOT_USERNAME = os.getenv("BOT_USERNAME")

REQUIRED_ENV = {
    "TELEGRAM_BOT_TOKEN": TELEGRAM_BOT_TOKEN,
    "TOKEN_GENIUS": TOKEN_GENIUS,
    "GOOGLE_YOUTUBE_API_KEY": GOOGLE_YOUTUBE_API_KEY,
}


def validate_env():
    missing = [k for k, v in REQUIRED_ENV.items() if not v]
    if missing:
        logger.critical("Missing required environment variables: %s", ", ".join(missing))
        sys.exit(1)
    logger.info("Environment validated — all required keys present")


genius = lyricsgenius.Genius(access_token=TOKEN_GENIUS, response_format="plain", timeout=12)
