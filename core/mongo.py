from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from config import MONGO_URI
from utils import LOGGER
import datetime

# MongoDB setup
LOGGER.info(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - INFO - Creating MONGO_CLIENT From MONGO_URL")
try:
    mongo_client = MongoClient(MONGO_URI)
    LOGGER.info(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - INFO - MONGO_CLIENT Successfully Created!")
except ConnectionFailure as e:
    LOGGER.error(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - ERROR - Failed to connect to MongoDB: {e}")
    raise

db = mongo_client["ItsSmartToolBot"]
users_collection = db["users"]
numbers_collection = db["numbers"]
authorized_users_collection = db["authorized_users"]