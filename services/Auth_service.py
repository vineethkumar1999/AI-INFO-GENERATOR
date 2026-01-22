from pymongo import MongoClient
from werkzeug.security import check_password_hash
from config.config import MONGO_URI, DB_NAME

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
users_collection = db["users"]

def verify_user(username, password):
    user = users_collection.find_one({"username": username})
    if not user:
        return False
    return check_password_hash(user["password_hash"], password)
