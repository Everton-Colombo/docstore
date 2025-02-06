# extensions.py
from pymongo import MongoClient
from config import Config

client = MongoClient(Config.MONGO_URI)
db = client.get_default_database()

# Collections used in the application.
data_collection = db.data
tenants_collection = db.tenants
