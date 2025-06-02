from fastapi_mcp import FastApiMCP
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from config import Database
from models import Professional, Slot, Patient, Appointment
from fastapi import HTTPException
from typing import List, Optional
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from models.specializations import MedicalSpecialization

from responses import SlotResponse, PatientResponse, CreateAppointmentDto, AppointmentResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    await Database.connect_db()
    yield
    await Database.close_db()

app = FastAPI(lifespan=lifespan)

@app.get("/slots/specialization/{specialization}", response_model=List[SlotResponse], operation_id="get_time_slots_by_specialization")
async def get_specialization_slots(
    specialization: MedicalSpecialization,
    start: datetime = datetime.now(),
    end: datetime = (datetime.now() + timedelta(days=30)), 
):
    """
    Get all slots for a given specialization.
    By default, it will return all slots available for the next 30 days.
    """
    
    if start > end:
        raise HTTPException(status_code=400, detail="Start date cannot exceed end date")

    db = Database.get_db()
    professionals = await Professional.get_many_by_query(db, {
        "specialization": specialization.value
    })
    if not professionals:
        raise HTTPException(status_code=404, detail="No professionals found for this specialization")

    professionals_dict = {str(professional.id): professional for professional in professionals}

    slots = await Slot.get_many_by_query(db, {
        "professional_id": {
            "$in": [ObjectId(professional.id) for professional in professionals]
        },
        "start_time": {
            "$gte": start.isoformat(),
            "$lte": end.isoformat()
        },
        "is_booked": False
    }, sort=[("start_time", 1)])

    return [SlotResponse.create(slot, professionals_dict[str(slot.professional_id)]) for slot in slots]



@app.get("/professionals/{professional_id}/slots", response_model=List[Slot], operation_id="get_time_slots")
async def get_professional_slots(
    professional_id: str,
    end: Optional[str] = None, 
    start: Optional[str] = None,
):
    db = Database.get_db()
    professional = await Professional.get_by_id(db, professional_id)
    if not professional:
        raise HTTPException(status_code=404, detail="Professional not found")
    
    
    start = datetime.now().isoformat() if not start else start
    time_filter = { "$gte": start }
    if end:
        time_filter["$lte"] = end

    slots = await Slot.get_many_by_query(db, {
        "professional_id": ObjectId(professional_id),
        "start_time": time_filter,
        "is_booked": False
    }, sort=[("start_time", 1)])

    return slots

@app.get("/patients/{national_id}", response_model=PatientResponse, operation_id="get_patient_by_national_id")
async def get_patient_by_national_id(national_id: str):
    """
    Get a patient's data by their national ID.
    """
    db = Database.get_db()
    patient = await Patient.get_one_by_query(db, {"national_id": national_id})
        
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    return PatientResponse.create(patient)

@app.post("/appointments", response_model=AppointmentResponse, operation_id="create_appointment")
async def create_appointment(appointment: CreateAppointmentDto):
    """
    Create a new appointment.
    """
    db = Database.get_db()
    
    patient = await Patient.get_by_id(db, appointment.patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    slot = await Slot.get_by_id(db, appointment.slot_id)
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    
    if slot.is_booked:
        raise HTTPException(status_code=400, detail="Slot is already booked")
    
    if slot.start_time < datetime.now():
        raise HTTPException(status_code=400, detail="Slot is in the past")

    professional = await Professional.get_by_id(db, slot.professional_id)
    if not professional:
        raise HTTPException(status_code=404, detail="Professional not found")

    new_appointment = Appointment(
        patient_id=appointment.patient_id,
        slot_id=appointment.slot_id
    )

    slot.is_booked = True
    await slot.save(db)

    try:
        await new_appointment.save(db)
    except Exception as e:
        slot.is_booked = False
        await slot.save(db)
        raise HTTPException(status_code=500, detail=str(e))

    return AppointmentResponse.create(new_appointment, patient, slot, professional)

mcp = FastApiMCP(app, include_operations=["get_time_slots"])
mcp.mount()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
