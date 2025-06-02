from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, UTC
from typing import Optional, TypeVar, Type, List
from pydantic_extra_types.mongo_object_id import MongoObjectId
from pymongo.asynchronous.database import AsyncDatabase
from bson.objectid import ObjectId

# TODO: move
class EmptyMongoObjectId(MongoObjectId):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return ""
    
    def __bool__(self):
        return False

    def __get_pydantic_core_schema__(self, *args, **kwargs):
        return None


T = TypeVar('T', bound='MongoBase')

class MongoBase(BaseModel):
    id: MongoObjectId = Field(alias="_id", default_factory=lambda: EmptyMongoObjectId())
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
        if isinstance(self.id, EmptyMongoObjectId):
            data.pop('_id', None)
        return {
            k: v for k, v in data.items()
            if v is not None
        }
    
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
    async def get_many_by_query(cls: Type[T], db: AsyncDatabase, query: dict, sort: Optional[List[tuple[str, int]]] = None) -> List[T]:
        """Get documents by query with optional sorting
        
        Args:
            db: AsyncDatabase instance
            query: MongoDB query dict
            sort: Optional list of tuples with (field_name, direction), where direction is 1 for ascending or -1 for descending
                 Example: [("created_at", -1)] to sort by created_at in descending order
        """
        collection_name = cls.get_collection_name()
        documents = []
        cursor = db[collection_name].find(query)
        if sort:
            cursor = cursor.sort(sort)
        async for document in cursor:
            documents.append(cls(**document))
        return documents
    
    @classmethod
    async def get_one_by_query(cls: Type[T], db: AsyncDatabase, query: dict) -> T | None:
        """Query a document by query"""
        collection_name = cls.get_collection_name()
        if document := await db[collection_name].find_one(query):
            return cls(**document)
        return None

    @classmethod
    async def get_by_id(cls: Type[T], db: AsyncDatabase, id: str) -> T | None:
        """Get a document by ID"""
        collection_name = cls.get_collection_name()
        if document := await db[collection_name].find_one({"_id": ObjectId(id)}):
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

    async def save(self, db: AsyncDatabase):
        """Save document to database"""
        self.updated_at = int(datetime.now(UTC).timestamp())
        collection_name = self.get_collection_name()
        
        if isinstance(self.id, EmptyMongoObjectId):
            self.created_at = self.updated_at
            result = await db[collection_name].insert_one(self.to_mongo())
            self.id = result.inserted_id
        else:
            await db[collection_name].update_one(
                {"_id": ObjectId(self.id)},
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