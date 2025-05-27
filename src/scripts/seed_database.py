import asyncio
from faker import Faker
import random
from typing import List
import sys
import os

from ..config.database import Database
from ..models import Patient, Professional, MedicalSpecialization

Faker.seed(12345)

NUM_PATIENTS = 50
NUM_PROFESSIONALS = 10

async def generate_random_patients(count: int) -> List[Patient]:
    fake = Faker()
    patients = []
    
    for _ in range(count):
        patient = Patient(
            _id=None,
            name=fake.name(),
            national_id=str(random.randint(100000000, 999999999)),  # 9-digit number
            phone_number=fake.phone_number(),
            email=fake.email()
        )
        patients.append(patient)
    
    return patients

async def generate_random_professionals(count: int) -> List[Professional]:
    fake = Faker()
    professionals = []
    
    for _ in range(count):
        professional = Professional(
            _id=None,
            name=fake.name(),
            specialization=random.choice(list(MedicalSpecialization))
        )
        professionals.append(professional)
    
    return professionals

async def seed_database():
    print(f"Connecting to database...")
    await Database.connect_db()
    
    try:
        db = Database.get_db()
        print(f"Generating {NUM_PATIENTS} random patients...")
        patients = await generate_random_patients(NUM_PATIENTS)
        
        print("Inserting patients into database...")
        # Convert patients to dictionaries and insert them
        patient_dicts = [patient.to_mongo() for patient in patients]
        result = await db.patients.insert_many(patient_dicts)
        
        print(f"Successfully inserted {len(result.inserted_ids)} patients!")

        print(f"Generating {NUM_PROFESSIONALS} random professionals...")
        professionals = await generate_random_professionals(NUM_PROFESSIONALS)
        
        print("Inserting professionals into database...")
        professional_dicts = [professional.to_mongo() for professional in professionals]
        result = await db.professionals.insert_many(professional_dicts)
        
        print(f"Successfully inserted {len(result.inserted_ids)} professionals!")
    
    finally:
        print("Closing database connection...")
        await Database.close_db()

if __name__ == "__main__":
    asyncio.run(seed_database()) 