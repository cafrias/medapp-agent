from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

from models.patient import Patient

class PatientResponse(BaseModel):
    id: str = Field(..., description="The unique identifier for the patient")
    name: str = Field(..., description="The name of the patient")
    national_id: str = Field(..., description="The national ID of the patient")
    email: str = Field(..., description="The email of the patient")
    phone_number: str = Field(..., description="The phone number of the patient")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "123456789",
                "name": "John Doe",
                "national_id": "123456789",
                "email": "john.doe@example.com",
                "phone_number": "+1234567890"
            }
        }
    }

    @classmethod
    def create(cls, patient: Patient):
        return cls(
            id=str(patient.id),
            name=patient.name,
            national_id=patient.national_id,
            email=patient.email,
            phone_number=patient.phone_number
        )
