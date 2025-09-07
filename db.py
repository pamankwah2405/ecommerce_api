import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get MongoDB connection string from environment variables
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "ecommerce")

ecommerce_db = None

try:
    if not MONGO_URI:
        raise ValueError("MONGO_URI environment variable not set.")
    # Connect to MongoDB
    mongo_client = MongoClient(MONGO_URI)
    mongo_client.admin.command('ping') # Check connection
    ecommerce_db = mongo_client[DB_NAME]

    print("✅ Successfully connected to MongoDB")

except (ConnectionFailure, ValueError) as e:
    print(f"❌ Error connecting to MongoDB: {e}")
