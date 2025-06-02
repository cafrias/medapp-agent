from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

from models.professional import Professional
from models.slot import Slot
from .professional_response import ProfessionalResponse

class SlotResponse(BaseModel):
    """
    A response model for a slot.
    """

    id: str  = Field(..., description="The ID of the slot")
    professional: ProfessionalResponse = Field(..., description="The professional associated with the slot")
    start_time: datetime = Field(..., description="The start time of the slot")
    end_time: datetime = Field(..., description="The end time of the slot")
    is_booked: bool = Field(..., description="Whether the slot is booked")
    
    model_config = {
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "example": {
                "id": "665656565656565656565656",
                "professional": {
                    "id": "665656565656565656565656",
                    "name": "John Doe",
                    "specialization": "Cardiology"
                },
                "start_time": "2024-03-20T09:00:00",
                "end_time": "2024-03-20T10:00:00",
                "is_booked": False
            }
        }
    }
    
    @classmethod
    def create(cls, slot: Slot, professional: Professional):
        return cls(
            id=str(slot.id),
            professional=ProfessionalResponse.from_professional(professional),
            start_time=slot.start_time,
            end_time=slot.end_time,
            is_booked=slot.is_booked,
        )
