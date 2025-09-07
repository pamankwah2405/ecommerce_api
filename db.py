# db.py
import os
from pymongo import MongoClient, errors
import certifi
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable not set.")
if not DB_NAME:
    raise ValueError("DB_NAME environment variable not set.")

# Use certifi for proper SSL/TLS certificates
tls_ca_file = certifi.where()

# Create MongoClient with SSL/TLS options
try:
    client = MongoClient(MONGO_URI, tlsCAFile=tls_ca_file, serverSelectionTimeoutMS=10000)
    # Test connection
    client.admin.command("ping")
    print("✅ Successfully connected to MongoDB Atlas")

except errors.ServerSelectionTimeoutError as err:
    print("❌ Could not connect to MongoDB Atlas:")
    print(err)
    raise SystemExit(err)

except errors.ConnectionFailure as err:
    print("❌ MongoDB connection failed:")
    print(err)
    raise SystemExit(err)

except Exception as e:
    print("❌ An unexpected error occurred:")
    print(e)
    raise SystemExit(e)

# Access the database
ecommerce_db = client[DB_NAME]
