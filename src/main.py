from contextlib import asynccontextmanager
from fastapi import FastAPI
from config import Database
from models import Patient
from typing import List
from responses.patient import PatientResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    await Database.connect_db()
    yield
    await Database.close_db()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/patients")
async def get_all_patients() -> List[Patient]:
    db = Database.get_db()
    patients = await Patient.get_all(db)
    return patients
