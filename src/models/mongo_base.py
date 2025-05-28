from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, UTC
from typing import Optional, TypeVar, Type, List
from pydantic_extra_types.mongo_object_id import MongoObjectId
from pymongo.asynchronous.database import AsyncDatabase


T = TypeVar('T', bound='MongoBase')

class MongoBase(BaseModel):
    id: Optional[MongoObjectId] = Field(None, alias="_id")
    created_at: int = Field(default_factory=lambda: int(datetime.now(UTC).timestamp()))
    updated_at: int = Field(default_factory=lambda: int(datetime.now(UTC).timestamp()))

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        from_attributes=True,
    )

    def to_mongo(self):
        """Convert to MongoDB document"""
        data = self.model_dump(by_alias=True)
        return {
            k: v for k, v in data.items()
            if v is not None
        }
    
    def get_id(self):
        if self.id:
            return self.id
        raise ValueError("ID is not set")

    @classmethod
    async def get_all(cls: Type[T], db) -> List[T]:
        """Get all documents from database"""
        documents = []
        collection_name = cls.get_collection_name()
        cursor = db[collection_name].find()
        async for document in cursor:
            documents.append(cls(**document))
        return documents

    @classmethod
    async def get_by_id(cls: Type[T], db, id: str) -> T | None:
        """Get a document by ID"""
        collection_name = cls.get_collection_name()
        if document := await db[collection_name].find_one({"_id": MongoObjectId(id)}):
            return cls(**document)
        return None
    
    @classmethod
    async def insert_many(cls: Type[T], db: AsyncDatabase, documents: List[T]):
        """Insert many documents into database, it updates the documents with the inserted ids"""
        collection_name = cls.get_collection_name()
        documents_dicts = [document.to_mongo() for document in documents]
        result = await db[collection_name].insert_many(documents_dicts)
        for i, document_id in enumerate(result.inserted_ids):
            documents[i].id = document_id
        return result

    async def save(self, db):
        """Save document to database"""
        self.updated_at = int(datetime.now(UTC).timestamp())
        collection_name = self.get_collection_name()
        
        if not self.id:
            self.created_at = self.updated_at
            result = await db[collection_name].insert_one(self.to_mongo())
            self.id = result.inserted_id
        else:
            await db[collection_name].update_one(
                {"_id": self.id},
                {"$set": self.to_mongo()}
            )
        return self

    async def delete(self, db) -> bool:
        """Delete document from database"""
        collection_name = self.get_collection_name()
        if self.id:
            await db[collection_name].delete_one({"_id": self.id})
            return True
        return False

    @classmethod
    def get_collection_name(cls) -> str:
        """Get the collection name for this model"""
        return f"{cls.__name__.lower()}s" 