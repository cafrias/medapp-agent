from datetime import datetime
from pydantic import Field, ConfigDict
from typing import Optional
from pydantic_extra_types.mongo_object_id import MongoObjectId

from .mongo_base import MongoBase

class Slot(MongoBase):
    start_time: datetime = Field(..., description="Start time of the slot")
    end_time: datetime = Field(..., description="End time of the slot")
    professional_id: MongoObjectId = Field(..., description="ID of the professional associated with this slot")
    is_booked: bool = Field(default=False, description="Whether the slot is already booked")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "start_time": "2024-03-20T09:00:00",
                "end_time": "2024-03-20T10:00:00",
                "professional_id": "507f1f77bcf86cd799439011",
                "is_booked": False
            }
        }
    )
