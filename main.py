from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import os

app = FastAPI()

# разрешаем доступ с WebApp
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FILE = "bookings.json"

def load_bookings():
    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_bookings(data):
    with open(FILE, "w") as f:
        json.dump(data, f)

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/busy")
def get_busy():
    bookings = load_bookings()
    busy = []
    for b in bookings:
        busy.append(f"{b['year']}-{str(b['month']).zfill(2)}-{str(b['day']).zfill(2)}")
    return busy

@app.post("/book")
def book(data: dict):
    bookings = load_bookings()

    start = data["checkin"]
    end = data["checkout"]

    bookings.append({
        "checkin": start,
        "checkout": end
    })

    save_bookings(bookings)

    return {"status": "booked"}


# 🔥 ВАЖНО ДЛЯ RAILWAY
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)