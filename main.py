from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json
import os
from datetime import datetime, timedelta

app = FastAPI()

BOOKINGS_FILE = "bookings.json"


# ---------- СОЗДАНИЕ ФАЙЛА ----------
if not os.path.exists(BOOKINGS_FILE):
    with open(BOOKINGS_FILE, "w") as f:
        json.dump([], f)


# ---------- МОДЕЛЬ ----------
class Booking(BaseModel):
    checkin: str
    checkout: str


# ---------- ЗАГРУЗКА ----------
def load_bookings():
    try:
        with open(BOOKINGS_FILE, "r") as f:
            return json.load(f)
    except:
        return []


# ---------- СОХРАНЕНИЕ ----------
def save_bookings(data):
    with open(BOOKINGS_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ---------- ROOT (чтобы не было Not Found) ----------
@app.get("/")
def root():
    return {"status": "API работает"}


# ---------- ЗАНЯТЫЕ ДАТЫ ----------
@app.get("/busy-dates")
def get_busy_dates():
    bookings = load_bookings()

    dates = []
    for b in bookings:
        try:
            d = f"{b['year']}-{str(b['month']).zfill(2)}-{str(b['day']).zfill(2)}"
            dates.append(d)
        except:
            continue

    return JSONResponse(dates)


# ---------- СОЗДАТЬ БРОНЬ ----------
@app.post("/book")
def create_booking(data: Booking):
    bookings = load_bookings()

    # защита от кривых данных
    if not data.checkin or not data.checkout:
        return {"error": "Нет дат"}

    try:
        start = datetime.fromisoformat(str(data.checkin)).date()
        end = datetime.fromisoformat(str(data.checkout)).date()
    except:
        return {"error": "Неверный формат даты"}

    if end <= start:
        return {"error": "Дата выезда должна быть позже"}

    # проверка занятости
    current = start
    while current < end:
        for b in bookings:
            if (
                b["day"] == current.day
                and b["month"] == current.month
                and b["year"] == current.year
            ):
                return {"error": "Даты заняты"}
        current += timedelta(days=1)

    # сохраняем
    current = start
    while current < end:
        bookings.append({
            "day": current.day,
            "month": current.month,
            "year": current.year
        })
        current += timedelta(days=1)

    save_bookings(bookings)

    return {"status": "ok"}


# ---------- УДАЛЕНИЕ БРОНИ (на будущее) ----------
@app.post("/cancel")
def cancel_booking(data: Booking):
    bookings = load_bookings()

    try:
        start = datetime.fromisoformat(str(data.checkin)).date()
        end = datetime.fromisoformat(str(data.checkout)).date()
    except:
        return {"error": "Ошибка даты"}

    new_bookings = []
    for b in bookings:
        date = datetime(b["year"], b["month"], b["day"]).date()
        if not (start <= date < end):
            new_bookings.append(b)

    save_bookings(new_bookings)

    return {"status": "cancelled"}