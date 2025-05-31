from pydantic import Field, ConfigDict

from .specializations import MedicalSpecialization
from .mongo_base import MongoBase

class Professional(MongoBase):
    name: str = Field(..., description="Full name of the professional")
    specialization: MedicalSpecialization = Field(..., description="Specialization of the professional")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "John Doe",
                "specialization": MedicalSpecialization.CARDIOLOGY.value
            }
        }
    )

    def to_mongo(self):
        """Convert to MongoDB document with proper enum handling"""
        data = super().to_mongo()
        if self.specialization:
            data["specialization"] = self.specialization.value
        return data

