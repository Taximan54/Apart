from fastapi import FastAPI
import json
import os

app = FastAPI()

BOOKINGS_FILE = "bookings.json"

def load_bookings():
    if not os.path.exists(BOOKINGS_FILE):
        return []
    with open(BOOKINGS_FILE, "r") as f:
        return json.load(f)

@app.get("/")
async def root():
    return {"status": "ok"}

@app.get("/busy")
async def get_busy_dates():
    bookings = load_bookings()
    busy = []

    for b in bookings:
        busy.append(f"{b['year']}-{str(b['month']).zfill(2)}-{str(b['day']).zfill(2)}")

    return busy