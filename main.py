from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json
import os
from datetime import datetime, timedelta

app = FastAPI()

BOOKINGS_FILE = "bookings.json"


# ---------- ЛОГИ ----------
def log(text):
    print(f"[LOG] {text}", flush=True)


# ---------- СОЗДАНИЕ ФАЙЛА ----------
if not os.path.exists(BOOKINGS_FILE):
    with open(BOOKINGS_FILE, "w") as f:
        json.dump([], f)
    log("Создан bookings.json")


# ---------- МОДЕЛЬ ----------
class Booking(BaseModel):
    checkin: str
    checkout: str


# ---------- ЗАГРУЗКА ----------
def load_bookings():
    try:
        with open(BOOKINGS_FILE, "r") as f:
            data = json.load(f)
            log(f"Загружено броней: {len(data)}")
            return data
    except Exception as e:
        log(f"Ошибка загрузки: {e}")
        return []


# ---------- СОХРАНЕНИЕ ----------
def save_bookings(data):
    try:
        with open(BOOKINGS_FILE, "w") as f:
            json.dump(data, f, indent=2)
        log(f"Сохранено броней: {len(data)}")
    except Exception as e:
        log(f"Ошибка сохранения: {e}")


# ---------- ROOT ----------
@app.get("/")
def root():
    log("Проверка API /")
    return {"status": "API работает"}


# ---------- ЗАНЯТЫЕ ДАТЫ ----------
@app.get("/busy-dates")
def get_busy_dates():
    log("Запрос /busy-dates")

    bookings = load_bookings()

    dates = []
    for b in bookings:
        try:
            d = f"{b['year']}-{str(b['month']).zfill(2)}-{str(b['day']).zfill(2)}"
            dates.append(d)
        except Exception as e:
            log(f"Ошибка формата даты: {e}")

    log(f"Отдаём занятые даты: {dates}")
    return JSONResponse(dates)


# ---------- СОЗДАТЬ БРОНЬ ----------
@app.post("/book")
def create_booking(data: Booking):
    log(f"POST /book получено: {data}")

    bookings = load_bookings()

    try:
        start = datetime.fromisoformat(str(data.checkin)).date()
        end = datetime.fromisoformat(str(data.checkout)).date()
        log(f"Даты: {start} → {end}")
    except Exception as e:
        log(f"Ошибка даты: {e}")
        return {"error": "Неверный формат даты"}

    if end <= start:
        log("Ошибка: выезд раньше заезда")
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
                log(f"Дата занята: {current}")
                return {"error": "Даты заняты"}
        current += timedelta(days=1)

    # сохранение
    current = start
    while current < end:
        bookings.append({
            "day": current.day,
            "month": current.month,
            "year": current.year
        })
        current += timedelta(days=1)

    save_bookings(bookings)

    log("Бронь успешно создана")
    return {"status": "ok"}


# ---------- ОТМЕНА ----------
@app.post("/cancel")
def cancel_booking(data: Booking):
    log(f"POST /cancel: {data}")

    bookings = load_bookings()

    try:
        start = datetime.fromisoformat(str(data.checkin)).date()
        end = datetime.fromisoformat(str(data.checkout)).date()
    except Exception as e:
        log(f"Ошибка даты: {e}")
        return {"error": "Ошибка даты"}

    new_bookings = []
    for b in bookings:
        date = datetime(b["year"], b["month"], b["day"]).date()
        if not (start <= date < end):
            new_bookings.append(b)

    save_bookings(new_bookings)

    log("Бронь отменена")
    return {"status": "cancelled"}