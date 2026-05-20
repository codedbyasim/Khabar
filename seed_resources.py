import psycopg2
import os
from dotenv import load_dotenv

load_dotenv('agents/.env')
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Check if location column exists
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'resources';")
columns = [row[0] for row in cur.fetchall()]

if 'location' not in columns:
    print("Adding location column to resources table...")
    cur.execute("ALTER TABLE resources ADD COLUMN location JSONB;")
    conn.commit()
    print("Column added.")
else:
    print("location column already exists.")

# Now insert multiple resources for Islamabad and Rawalpindi
resources_to_insert = [
    ("RES-RWP-01", "Faizabad Main Ambulance Unit", "ambulance", 5, "available", {"lat": 33.6375, "lng": 73.0784}),
    ("RES-RWP-02", "Saddar WASA Flood Response", "dewatering_pump", 4, "available", {"lat": 33.5984, "lng": 73.0544}),
    ("RES-RWP-03", "Holy Family Medical Rescue", "rescue_team", 3, "available", {"lat": 33.6341, "lng": 73.0715}),
    ("RES-RWP-04", "Commercial Market Fire Dept", "fire_truck", 2, "available", {"lat": 33.6338, "lng": 73.0747}),
    ("RES-RWP-05", "Peshawar Road Quick Response", "rescue_team", 2, "available", {"lat": 33.6063, "lng": 73.0233}),
    ("RES-ISB-01", "G-11 Fire & Rescue Unit", "fire_truck", 4, "available", {"lat": 33.6766, "lng": 73.0132}),
    ("RES-ISB-02", "F-6 Emergency Ambulances", "ambulance", 3, "available", {"lat": 33.7299, "lng": 73.0746}),
    ("RES-ISB-03", "E-11 WASA Dewatering Point", "dewatering_pump", 3, "available", {"lat": 33.7001, "lng": 72.9812}),
    ("RES-ISB-04", "Blue Area Central Rescue", "rescue_team", 5, "available", {"lat": 33.7182, "lng": 73.0605}),
    ("RES-ISB-05", "I-8 Traffic Management", "police_unit", 2, "available", {"lat": 33.6698, "lng": 73.0741}),
    ("RES-ISB-06", "PIMS Hospital Ambulances", "ambulance", 8, "available", {"lat": 33.7051, "lng": 73.0504}),
]

import json
for r in resources_to_insert:
    cur.execute('''
        INSERT INTO resources (resource_id, name, type, quantity, status, location)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (resource_id) DO UPDATE SET
            name = EXCLUDED.name,
            quantity = EXCLUDED.quantity,
            location = EXCLUDED.location;
    ''', (r[0], r[1], r[2], r[3], r[4], json.dumps(r[5])))

conn.commit()
cur.close()
conn.close()
print("Resources inserted successfully!")
