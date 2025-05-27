from pymongo import AsyncMongoClient
from typing import Optional
from src.constants import DB_NAME

class Database:
    client: Optional[AsyncMongoClient] = None
    
    @classmethod
    async def connect_db(cls):
        cls.client = AsyncMongoClient("mongodb://localhost:27017")
        
    @classmethod
    async def close_db(cls):
        if cls.client is not None:
            await cls.client.close()
            
    @classmethod
    def get_db(cls):
        if cls.client is None:
            raise Exception("Database not connected")
        return cls.client[DB_NAME]