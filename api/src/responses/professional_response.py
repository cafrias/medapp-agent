from pydantic import BaseModel, Field

from models.professional import Professional

class ProfessionalResponse(BaseModel):
    """
    A response model for a professional.
    """

    id: str = Field(..., description="The ID of the professional")
    name: str = Field(..., description="The name of the professional")
    specialization: str = Field(..., description="The specialization of the professional")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "665656565656565656565656",
                "name": "John Doe",
                "specialization": "Cardiology"
            }
        }
    }

    @classmethod
    def from_professional(cls, professional: Professional):
        return cls(
            id=str(professional.id),
            name=professional.name,
            specialization=professional.specialization.value)
