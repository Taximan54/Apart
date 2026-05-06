import sqlite3
from datetime import datetime, timedelta
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 🔓 разрешаем WebApp доступ
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB = "bookings.db"

# ---------- INIT DB ----------
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id TEXT,
        user INTEGER,
        date TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------- ПОЛУЧИТЬ ЗАНЯТЫЕ ----------
@app.get("/busy")
def get_busy():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("SELECT date FROM bookings")
    rows = c.fetchall()

    conn.close()

    return [r[0] for r in rows]

# ---------- СОЗДАТЬ БРОНЬ ----------
@app.post("/book")
def book(data: dict):
    start = datetime.fromisoformat(data["checkin"])
    end = datetime.fromisoformat(data["checkout"])
    user = data.get("user", 0)

    booking_id = data.get("id")

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    current = start
    while current < end:
        c.execute(
            "INSERT INTO bookings VALUES (?, ?, ?)",
            (booking_id, user, current.strftime("%Y-%m-%d"))
        )
        current += timedelta(days=1)

    conn.commit()
    conn.close()

    return {"status": "ok"}

# ---------- МОИ БРОНИ ----------
@app.get("/my/{user}")
def my(user: int):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("SELECT id, date FROM bookings WHERE user=?", (user,))
    rows = c.fetchall()

    conn.close()

    result = {}
    for bid, d in rows:
        result.setdefault(bid, []).append(d)

    out = []
    for bid, dates in result.items():
        dates.sort()
        out.append({
            "id": bid,
            "start": dates[0],
            "end": dates[-1]
        })

    return out

# ---------- ОТМЕНА ----------
@app.delete("/cancel/{bid}")
def cancel(bid: str):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("DELETE FROM bookings WHERE id=?", (bid,))

    conn.commit()
    conn.close()

    return {"status": "deleted"}

import os
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)