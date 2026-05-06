import asyncio
import json
import uuid
import os

from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, WebAppInfo
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

TOKEN = "8770383990:AAFOOWKAzZbEVWzXvRO_j_V0wIg19wzrNvw"
ADMIN_ID = 1008661058

bot = Bot(token=TOKEN)
dp = Dispatcher()

BOOKINGS_FILE = "bookings.json"

# создать файл если нет
if not os.path.exists(BOOKINGS_FILE):
    with open(BOOKINGS_FILE, "w") as f:
        json.dump([], f)


def load_bookings():
    with open(BOOKINGS_FILE, "r") as f:
        return json.load(f)


def save_bookings(data):
    with open(BOOKINGS_FILE, "w") as f:
        json.dump(data, f)


# API
app = FastAPI()

@app.get("/busy-dates")
def busy_dates():
    bookings = load_bookings()
    dates = []

    for b in bookings:
        date = f"{b['year']}-{str(b['month']).zfill(2)}-{str(b['day']).zfill(2)}"
        dates.append(date)

    return JSONResponse(dates)


# бот
@dp.message(CommandStart())
async def start(message: Message):

    kb = ReplyKeyboardBuilder()

    kb.button(
        text="📅 Открыть календарь",
        web_app=WebAppInfo(
            url="https://zingy-bunny-c82244.netlify.app/"
        )
    )

    kb.adjust(1)

    await message.answer("Выбери даты:", reply_markup=kb.as_markup(resize_keyboard=True))


@dp.message(lambda m: m.web_app_data)
async def webapp_booking(message: Message):

    data = json.loads(message.web_app_data.data)

    checkin = data.get("checkin")
    checkout = data.get("checkout")

    bookings = load_bookings()

    booking_id = str(uuid.uuid4())[:8]

    start = datetime.fromisoformat(checkin).date()
    end = datetime.fromisoformat(checkout).date()

    current = start
    while current < end:
        bookings.append({
            "id": booking_id,
            "day": current.day,
            "month": current.month,
            "year": current.year
        })
        current += timedelta(days=1)

    save_bookings(bookings)

    await message.answer(f"✅ Бронь {start} → {end}")

    await message.bot.send_message(
        ADMIN_ID,
        f"🔥 Новая бронь\n{start} → {end}"
    )


async def start_bot():
    await dp.start_polling(bot)


def start_api():
    uvicorn.run(app, host="0.0.0.0", port=8000)


async def main():
    loop = asyncio.get_event_loop()
    loop.create_task(start_bot())

    await asyncio.to_thread(start_api)


if __name__ == "__main__":
    asyncio.run(main())