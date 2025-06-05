from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from src.deepseek_llm import DeepSeekLLM
from src.database import get_db
from src.availability_logic import check_availability,add_booking
import json
import re  # ✅ Required for cleaning the response

router = APIRouter()

class QuestionRequest(BaseModel):
    question: str

@router.post("/ask_llm/")
async def ask_llm(request: QuestionRequest, db=Depends(get_db)):
    question = request.question
    llm = DeepSeekLLM()

    prompt = f"""
You are an intelligent assistant that helps manage room bookings.

From the following user request:
\"{question}\"

Extract the **action** and its corresponding **parameters** in **strict JSON format**.

Supported actions:
- "check_availability"
- "add_booking"
- "cancel_booking"

Required JSON structure:
{{
  "action": "check_availability" | "add_booking" | "cancel_booking",
  "parameters": {{
    "room_name": "...",
    "date": "yyyy-mm-dd",
    "start_time": "HH:MM",
    "end_time": "HH:MM",
    "booking_id": "..."  # Only needed for cancel_booking
  }}
}}

Respond in **only JSON format**, without explanations.
"""


    try:
        llm_response = llm._call(prompt)
        print("Raw LLM response:", llm_response)

        
        cleaned_response = re.sub(r"^```json|```$", "", llm_response.strip(), flags=re.MULTILINE).strip()
        print("Cleaned LLM response:", cleaned_response)

       
        # data = json.loads(cleaned_response)
        parsed = json.loads(cleaned_response)

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Error parsing LLM output: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM call failed: {str(e)}")

    action = parsed.get("action")
    params = parsed.get("parameters", {})
    
# change llm promt, cehcke what are the rooms befare llm output.
    if action == "check_availability":
        return check_availability(
        room_name=params["room_name"],
        date=params["date"],
        start_time=params["start_time"],
        end_time=params["end_time"],
        db=db,
    )

    elif action == "add_booking":
        return add_booking(
        room_name=params["room_name"],
        date=params["date"],
        start_time=params["start_time"],
        end_time=params["end_time"],
        created_by=params.get("created_by", "system"),
        db=db,
    )

    else:
        raise HTTPException(status_code=400, detail=f"Unsupported action: {action}")



    # elif action == "add_booking":
    #     is_available = check_availability(
    #         room_name=params["room_name"],
    #         date=params["date"],
    #         start_time=params["start_time"],
    #         end_time=params["end_time"],
    #         db=db,
    #     )
    #     if is_available.get("available"):
    #         return add_booking(
    #             room_name=params["room_name"],
    #             date=params["date"],
    #             start_time=params["start_time"],
    #             end_time=params["end_time"],
    #             db=db,
    #         )
    #     else:
    #         return suggest_alternatives(
    #             date=params["date"],
    #             start_time=params["start_time"],
    #             end_time=params["end_time"],
    #             db=db,
    #         )

    # elif action == "cancel_booking":
    #     booking_id = params.get("booking_id")
    #     if not booking_id:
    #         raise HTTPException(status_code=400, detail="Missing 'booking_id' for cancellation.")
    #     return cancel_booking(booking_id=booking_id, db=db)

    # else:
    #     raise HTTPException(status_code=400, detail=f"Unsupported action: {action}")
    # required_fields = ["room_name", "date", "start_time", "end_time"]
    # missing = [f for f in required_fields if f not in data]
    # if missing:
    #     raise HTTPException(status_code=400, detail=f"Missing fields from LLM output: {missing}")

    # return check_availability(
    #     room_name=data["room_name"],
    #     date=data["date"],
    #     start_time=data["start_time"],
    #     end_time=data["end_time"],
    #     db=db,
    # )

# in this code we used multy intents not crew ai.
# With Crew AI:
#we can do it like this with crew ai

# check_availability_agent checks LT1

# If not available, room_list_agent is triggered

# Optionally, a fallback_agent suggests alternatives