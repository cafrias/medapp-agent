from pydantic import BaseModel, Field
from pydantic_extra_types.mongo_object_id import MongoObjectId

class CreateAppointmentDto(BaseModel):
    patient_id: MongoObjectId = Field(..., description="The ID of the patient")
    slot_id: MongoObjectId = Field(..., description="The ID of the slot")

    model_config = {
        "json_schema_extra": {
            "example": {
                "patient_id": "507f1f77bcf86cd799439011",
                "slot_id": "507f1f77bcf86cd799439011"
            }
        }
    }
