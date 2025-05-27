#!/bin/bash

DB_NAME="medapp"

# Drop the database
docker compose exec mongodb mongosh --eval "db.getSiblingDB(\"$DB_NAME\").dropDatabase()"

# Seed the database
poetry run python -m src.scripts.seed_database