import asyncio
from datetime import timedelta
from faker import Faker
import random
from typing import List
import sys
import os

from ..config.database import Database
from ..models import Patient, Professional, MedicalSpecialization, Slot, Appointment

Faker.seed(12345)

NUM_PATIENTS = 50
NUM_PROFESSIONALS = 10
NUM_SLOTS = 100
NUM_APPOINTMENTS = 10

async def generate_random_patients(count: int) -> List[Patient]:
    fake = Faker()
    patients = []
    
    for _ in range(count):
        patient = Patient(
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
            name=fake.name(),
            specialization=random.choice(list(MedicalSpecialization))
        )
        professionals.append(professional)
    
    return professionals

async def generate_random_slots(count: int, professionals: List[Professional]) -> List[Slot]:
    fake = Faker()
    slots = []
        
    for _ in range(count):
        start_time = fake.date_time_between(start_date='+1d', end_date='+30d')
        end_time = start_time + timedelta(minutes=30)

        slot = Slot(
            start_time=start_time,
            end_time=end_time,
            professional_id=random.choice(professionals).id,
            is_booked=random.choice([True, False])
        )
        slots.append(slot)

    return slots

async def generate_random_appointments(db, count: int, slots: List[Slot], patients: List[Patient]) -> List[Appointment]:
    appointments = []
    
    for _ in range(count):
        slot = random.choice(slots)
        while slot.is_booked:
            slot = random.choice(slots)
        
        slot.is_booked = True
        await slot.save(db)
        
        appointment = Appointment(
            patient_id=random.choice(patients).id,
            slot_id=random.choice(slots).id
        )
        appointments.append(appointment)
    
    return appointments

async def seed_database():
    print(f"Connecting to database...")
    await Database.connect_db()
    
    try:
        db = Database.get_db()
        print(f"Generating {NUM_PATIENTS} random patients...")
        patients = await generate_random_patients(NUM_PATIENTS)
        
        print("Inserting patients into database...")
        result = await Patient.insert_many(db, patients)
        print(f"Successfully inserted {len(result.inserted_ids)} patients!")

        print(f"Generating {NUM_PROFESSIONALS} random professionals...")
        professionals = await generate_random_professionals(NUM_PROFESSIONALS)
        
        print("Inserting professionals into database...")
        result = await Professional.insert_many(db, professionals)
        print(f"Successfully inserted {len(result.inserted_ids)} professionals!")
 
        print(f"Generating {NUM_SLOTS} random slots...")
        slots = await generate_random_slots(NUM_SLOTS, professionals)
        
        print("Inserting slots into database...")
        result = await Slot.insert_many(db, slots)
        print(f"Successfully inserted {len(result.inserted_ids)} slots!")

        print(f"Generating {NUM_APPOINTMENTS} random appointments...")
        appointments = await generate_random_appointments(db, NUM_APPOINTMENTS, slots, patients)
        
        print("Inserting appointments into database...")
        result = await Appointment.insert_many(db, appointments)
        print(f"Successfully inserted {len(result.inserted_ids)} appointments!")
    
    finally:
        print("Closing database connection...")
        await Database.close_db()

if __name__ == "__main__":
    asyncio.run(seed_database()) 