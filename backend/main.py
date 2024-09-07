from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime


app = FastAPI()

class Workout(BaseModel):
    id: str | None = None
    date: str
    start_time: str
    duration: float
    workout_type: str | None = None
    calories_burned: int | None = None
    notes: str | None = None

# in practice: SQL database
workouts_db: list[dict] = []

@app.get("/")
async def root():
    return {"message": "Welcome to the App Team Takehome! Made with <3 by Mihir Sharma."}

@app.post("/create", status_code=201)
async def create(workout: Workout):
    # Data validation
    try:
        datetime.strptime(workout.date, '%d-%m-%y')
    except ValueError:
        raise HTTPException(400, "Bad Request: Date is in the wrong format. Should be in DD-MM-YY")
    
    try:
        datetime.strptime(workout.start_time, '%H-%M')
    except ValueError:
        raise HTTPException(400, "Bad request: Time must be in the format HH-MM")
    
    if workout.duration <= 0:
        raise HTTPException(400, "duration cannot be negative")
    if workout.calories_burned < 0:
        raise HTTPException(400, "Calories burned cannot be less than 0")
    
    # assigning the workout id

    # if they assign an id, overwrite it because we should be handling that internally
    workout.id = str(uuid4())
    
    workout_record = workout.model_dump()
    workouts_db.append(workout_record)

    return {
        "status" : "success",
        "message": "Created sucessfully!",
        "workout": workout
    }

@app.get("/search", status_code=200)
async def get_workouts(date: str | None = None, workout_type: str | None = None, note_keyword: str | None = None):
    
    filtered = workouts_db

    if date:
        try:
            datetime.strptime(date, "%d-%m-%y")
        except ValueError:
            raise HTTPException(400, "date is not in valid format")
        
        filtered = [w for w in filtered if w["date"] == date]
    
    if workout_type:
        filtered = [w for w in filtered if w["workout_type"] == workout_type]

    if note_keyword:
        filtered = [w for w in filtered if w["notes"] and note_keyword in w["notes"]]

    return filtered


@app.get("/total/{category}", status_code=200)
async def calculate_total(category):
    try:
        if not workouts_db:
            raise ValueError("Workout DB is empty")

        valid_attributes = Workout.model_fields.keys()
        if category not in valid_attributes:
            raise ValueError(f"{category} is not a valid category")
        
        if not all(isinstance(w.get(category), (int, float)) for w in workouts_db if w.get(category) is not None):
            raise ValueError(f"Category '{category}' cannot be summed, must be numeric (int or float)")
        
        total = sum(w[category] for w in workouts_db if w[category] is not None)
        return {
            "category" : category,
            "total" : total
        }
    except ValueError as e:
        raise HTTPException(400, str(e))

    

    