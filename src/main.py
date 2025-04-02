# from fastapi import FastAPI

# app = FastAPI()

# @app.get("/")
# def read_root():
#     return {"message": "Hello World"}






# from fastapi import FastAPI, Depends, HTTPException
# # from sqlalchemy.orm import Session
# # # from datetime import date, time
# # # from database import SessionLocal, Hall, Booking
# # from datetime import datetime
# # from sqlalchemy import and_

# # from models import MRBSEntry, MRBSRoom  # Assuming you have SQLAlchemy models for these tables
# # from database import get_db







# from datetime import datetime
# from fastapi import Depends, HTTPException
# from sqlalchemy.orm import Session
# from models import MRBSEntry, MRBSRoom
# from database import get_db

# app = FastAPI()

# def get_database():
#     from database import get_db  # Import inside function to avoid circular import
#     return get_db()

# @app.get("/check_availability/")
# def check_availability(room_name: str, date: date, start_time: time, end_time: time, db: Session = Depends(get_db)):
#     # Convert date and time to Unix timestamps
#     start_timestamp = int(datetime.combine(date, start_time).timestamp())
#     end_timestamp = int(datetime.combine(date, end_time).timestamp())

#     # Find the room ID
#     room = db.query(MRBSRoom).filter(MRBSRoom.room_name == room_name).first()
#     if not room:
#         raise HTTPException(status_code=404, detail="Room not found")

#     # Check if there's an overlapping booking
#     existing_booking = (
#         db.query(MRBSEntry)
#         .filter(
#             MRBSEntry.room_id == room.id,
#             MRBSEntry.start_time < end_timestamp,
#             MRBSEntry.end_time > start_timestamp
#         )
#         .first()
#     )

#     if existing_booking:
#         return {"message": f"{room_name} is NOT available at this time"}
    
#     return {"message": f"{room_name} is available. You can book it."}



# # @app.post("/book/")
# # def book_hall(user_id: int, hall_name: str, date: date, start_time: time, end_time: time, db: Session = Depends(get_db)):
# #     # Find the hall
# #     hall = db.query(Hall).filter(Hall.name == hall_name).first()
# #     if not hall:
# #         raise HTTPException(status_code=404, detail="Hall not found")

# #     # Check if hall is available
# #     existing_booking = (
# #         db.query(Booking)
# #         .filter(Booking.hall_id == hall.id, Booking.date == date)
# #         .filter(
# #             (Booking.start_time < end_time) & (Booking.end_time > start_time)
# #         )
# #         .first()
# #     )

# #     if existing_booking:
# #         raise HTTPException(status_code=400, detail="Hall is already booked")

# #     # Book the hall
# #     new_booking = Booking(user_id=user_id, hall_id=hall.id, date=date, start_time=start_time, end_time=end_time, status="Confirmed")
# #     db.add(new_booking)
# #     db.commit()

# #     return {"message": f"{hall_name} booked successfully for {date} from {start_time} to {end_time}"}
# # def send_notification(user_id: int, message: str):
# #     # Simulating a notification system
# #     print(f"Notification sent to User {user_id}: {message}")

# # @app.post("/notify/")
# # def notify_user(user_id: int, message: str):
# #     send_notification(user_id, message)
# #     return {"message": "Notification sent successfully"}

from datetime import datetime, date, time
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from src.models import MRBSEntry, MRBSRoom
from src.database import get_db
import logging

# ✅ Define FastAPI app at the top
app = FastAPI()
 # Make sure this file exists!




# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

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

@app.get("/test/")
def test_api():
    return {"message": "FastAPI is working!"}
