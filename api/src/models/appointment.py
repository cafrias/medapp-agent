
from datetime import datetime
from pydantic import Field, ConfigDict
from typing import Optional
from pydantic_extra_types.mongo_object_id import MongoObjectId
from pymongo.asynchronous.database import AsyncDatabase

from .mongo_base import MongoBase

class Appointment(MongoBase):
    patient_id: MongoObjectId = Field(..., description="ID of the patient associated with this appointment")
    slot_id: MongoObjectId = Field(..., description="ID of the slot associated with this appointment")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "patient_id": "507f1f77bcf86cd799439011",
                "slot_id": "507f1f77bcf86cd799439011"
            }
        }
    )
