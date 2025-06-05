from datetime import datetime, date, time
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from src.models import MRBSEntry, MRBSRoom
from src.database import get_db
import logging
import os
from langchain_core.language_models import BaseLLM
from langchain_core.outputs import LLMResult, Generation
import requests
from pydantic import Field
from typing import Optional, List, Any
from src.api import router 
from src.deepseek_llm import DeepSeekLLM

# Your DeepSeekLLM class definition here (copy your class code exactly)

# ✅ Define FastAPI app at the top
app = FastAPI()
 # Make sure this file exists!


app.include_router(router)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

from bs4 import BeautifulSoup
import requests



# @app.get("/scrape_mrbs/")
# def scrape_mrbs(
#     year: int = Query(..., example=2025),
#     month: int = Query(..., example=4),
#     day: int = Query(..., example=30),
#     area: int = Query(..., example=2),
#     room: int = Query(..., example=26)
# ):
#     """
#     Scrapes MRBS booking records from the day.php page and returns them as JSON.
#     """

#     # 1. Build the URL dynamically
#     url = f"http://localhost/foemrbs/day.php?year={year}&month={month:02d}&day={day:02d}&area={area}&room={room}"

#     try:
#         # 2. Send HTTP GET request
#         response = requests.get(url)

#         if response.status_code != 200:
#             raise HTTPException(status_code=502, detail=f"Failed to fetch MRBS page. HTTP {response.status_code}")

#         # 3. Parse HTML using BeautifulSoup
#         soup = BeautifulSoup(response.text, 'html.parser')

#         # ⚠️ 4. Find booking elements — UPDATE this selector based on your MRBS HTML structure
#         bookings = soup.find_all("div", class_="booking")  # Adjust if needed

#         result = []

#         for booking in bookings:
#             # 5. Extract booking info — adapt this based on your HTML layout
#             data = booking.text.strip().replace("\n", " ").replace("\r", "")
#             result.append({"text": data})

#         return {"date": f"{year}-{month:02d}-{day:02d}", "room": room, "bookings": result}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error scraping MRBS: {str(e)}")

@app.get("/check_availability/")
def check_availability(room_name: str, date: date, start_time: str, end_time: str, db: Session = Depends(get_db)):
    print(f"🔵 Received Input -> room_name: {room_name}, date: {date}, start_time: {start_time}, end_time: {end_time}")

    # Strip newline characters and spaces (if any)
    start_time = start_time.strip()
    end_time = end_time.strip()
    print(f"🟢 Cleaned Input -> start_time: {start_time}, end_time: {end_time}")

    # Convert start_time and end_time to `time` objects
    try:
        start_time_obj = datetime.strptime(start_time, "%H:%M").time()
        end_time_obj = datetime.strptime(end_time, "%H:%M").time()
        print(f"🟡 Parsed Time -> start_time_obj: {start_time_obj}, end_time_obj: {end_time_obj}")
    except ValueError as e:
        print(f"🔴 Time Parsing Error: {e}")
        raise HTTPException(status_code=400, detail="Invalid time format. Use HH:MM.")

    # Convert date and time to timestamps
    start_timestamp = int(datetime.combine(date, start_time_obj).timestamp())
    end_timestamp = int(datetime.combine(date, end_time_obj).timestamp())
    print(f"🟣 Converted Timestamps -> start_timestamp: {start_timestamp}, end_timestamp: {end_timestamp}")

    # Check if the room exists
    room = db.query(MRBSRoom).filter(MRBSRoom.room_name == room_name).first()
    if not room:
        print(f"🔴 Room '{room_name}' not found")
        raise HTTPException(status_code=404, detail="Room not found")

    print(f"✅ Room Found -> room_id: {room.id}")

    # Check for overlapping bookings
    existing_booking = (
        db.query(MRBSEntry)
        .filter(
            MRBSEntry.room_id == room.id,
            MRBSEntry.start_time < end_timestamp,
            MRBSEntry.end_time > start_timestamp
        )
        .first()
    )

    if existing_booking:
        print(f"❌ Room '{room_name}' is NOT available at this time")
        return {"message": f"{room_name} is NOT available at this time"}
    
    print(f"✅ Room '{room_name}' is available for booking")
    return {"message": f"{room_name} is available. You can book it."}

# @app.get("/test/")
# def test_api():
#     return {"message": "FastAPI is working!"}

# @app.on_event("startup")
# async def check_deepseek_llm():
#     print("Checking DeepSeek LLM configuration...")

#     try:
#         llm = DeepSeekLLM()
#         # Run a simple prompt to verify
#         response = llm._call("Hello")
#         print("✅ DeepSeek LLM is configured correctly. Sample response:")
#         print(response)
#     except Exception as e:
#         print(f"❌ DeepSeek LLM configuration failed: {e}")