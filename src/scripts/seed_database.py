import asyncio
from faker import Faker
import random
from typing import List
import sys
import os

from ..config.database import Database
from ..models.patient import Patient

# # Add the src directory to the Python path so we can import our modules
# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# from src.models.patient import Patient
# from src.config.database import Database

async def generate_random_patients(count: int) -> List[Patient]:
    fake = Faker()
    # Set a fixed seed for reproducible data
    Faker.seed(12345)
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

async def seed_database(num_patients: int = 50):
    print(f"Connecting to database...")
    await Database.connect_db()
    
    try:
        db = Database.get_db()
        print(f"Generating {num_patients} random patients...")
        patients = await generate_random_patients(num_patients)
        
        print("Inserting patients into database...")
        # Convert patients to dictionaries and insert them
        patient_dicts = [patient.to_mongo() for patient in patients]
        result = await db.patients.insert_many(patient_dicts)
        
        print(f"Successfully inserted {len(result.inserted_ids)} patients!")
    
    finally:
        print("Closing database connection...")
        await Database.close_db()

if __name__ == "__main__":
    asyncio.run(seed_database()) 