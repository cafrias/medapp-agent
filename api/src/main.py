import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from config import Database
from models import Professional, Slot
from fastapi import HTTPException
from typing import List
from bson.objectid import ObjectId
from datetime import datetime

@asynccontextmanager
async def lifespan(app: FastAPI):
    await Database.connect_db()
    yield
    await Database.close_db()

app = FastAPI(lifespan=lifespan)

@app.get("/professionals/{professional_id}/slots", response_model=List[Slot])
async def get_professional_slots(
    professional_id: str,
    end: str, 
    start: str,
):
    db = Database.get_db()
    professional = await Professional.get_by_id(db, professional_id)
    if not professional:
        raise HTTPException(status_code=404, detail="Professional not found")
    
    
    start = datetime.now().isoformat() if start == "" else start
    time_filter = { "$gte": start }
    if end != "":
        time_filter["$lte"] = end

    slots = await Slot.get_many_by_query(db, {
        "professional_id": ObjectId(professional_id),
        "start_time": time_filter,
        "is_booked": False
    }, sort=[("start_time", 1)])

    return slots


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
