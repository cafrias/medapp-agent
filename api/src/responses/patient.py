from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class PatientResponse(BaseModel):
    id: str
    name: str
    national_id: str
    phone_number: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "from_attributes": True
    }
