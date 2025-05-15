from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN
from utils import LOGGER
import datetime

# Bot client setup
LOGGER.info(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - INFO - Creating Bot Client From BOT_TOKEN")
try:
    bot = Client("twilio_async_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
    LOGGER.info(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - INFO - Bot Client Created Successfully!")
except Exception as e:
    LOGGER.error(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - ERROR - Failed to create bot client: {e}")
    raise