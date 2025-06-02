from datetime import datetime
from pydantic import BaseModel, Field
from pydantic_extra_types.mongo_object_id import MongoObjectId
from models import Appointment, Slot, Professional, Patient, MedicalSpecialization

class ProfessionalSummary(BaseModel):
    id: MongoObjectId = Field(..., description="The ID of the professional")
    name: str = Field(..., description="The name of the professional")
    specialization: MedicalSpecialization = Field(..., description="The specialization of the professional")

class PatientSummary(BaseModel):
    id: MongoObjectId = Field(..., description="The ID of the patient")
    name: str = Field(..., description="The name of the patient")
    national_id: str = Field(..., description="The national ID of the patient")

class SlotSummary(BaseModel):
    id: MongoObjectId = Field(..., description="The ID of the slot")
    start_time: datetime = Field(..., description="The start time of the slot")
    end_time: datetime = Field(..., description="The end time of the slot")

class AppointmentResponse(BaseModel):
    id: MongoObjectId = Field(..., description="The ID of the appointment")
    patient: PatientSummary = Field(..., description="The patient associated with the appointment")
    slot: SlotSummary = Field(..., description="The slot associated with the appointment")
    professional: ProfessionalSummary = Field(..., description="The professional associated with the slot")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "patient": {"id": "507f1f77bcf86cd799439011", "name": "John Doe", "national_id": "1234567890"},
                "slot": {"id": "507f1f77bcf86cd799439011", "start_time": "2024-03-20T09:00:00", "end_time": "2024-03-20T10:00:00"},
                "professional": {"id": "507f1f77bcf86cd799439011", "name": "John Doe", "specialization": "cardiology"}
            }
        }
    }
    
    @classmethod
    def create(cls, appointment: Appointment, patient: Patient, slot: Slot, professional: Professional):
        return cls(
            id=appointment.id,
            patient=PatientSummary(
                id=appointment.patient_id,
                name=patient.name,
                national_id=patient.national_id
            ),
            slot=SlotSummary(
                id=appointment.slot_id,
                start_time=slot.start_time,
                end_time=slot.end_time
            ),
            professional=ProfessionalSummary(
                id=professional.id,
                name=professional.name,
                specialization=professional.specialization
            )
        )
