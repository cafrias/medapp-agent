from pydantic import Field, ConfigDict
from .mongo_base import MongoBase

class Patient(MongoBase):
    name: str = Field(..., description="Full name of the patient")
    national_id: str = Field(..., description="National identification number of the patient")
    phone_number: str = Field(..., description="Contact phone number of the patient")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "John Doe",
                "national_id": "123456789",
                "phone_number": "+1234567890"
            }
        }
    )
