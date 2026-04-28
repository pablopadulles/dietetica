from motor.motor_asyncio import AsyncIOMotorClient
import os

class Database:
    def __init__(self):
        self.client = None
        self.db = None
        self.productos_collection = None

    def connect(self):
        self.client = AsyncIOMotorClient(os.getenv("MONGO_URL", "mongodb://localhost:27017"), maxPoolSize=50, minPoolSize=5)
        self.db = self.client["dietetica"]
        self.productos_collection = self.db["productos"]

    def disconnect(self):
        if self.client:
            self.client.close()

db = Database()
