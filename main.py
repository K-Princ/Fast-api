from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal
import json

app = FastAPI()

class Patient(BaseModel):
    id: Annotated[str, Field(..., description="The ID of the patient", example="P001")]
    name: Annotated[str, Field(..., description="The name of the patient", example="John Doe")]
    city: Annotated[str, Field(..., description="The city of the patient", example="New York")]
    age: Annotated[int, Field(..., gt = 0, lt = 120, description="The age of the patient", example=30)]
    gender: Annotated[Literal['Male', 'Female', 'Other'], Field(..., description="The gender of the patient", example="Male")]
    height: Annotated[float, Field(..., gt = 0, description="The height of the patient in meters", example=1.75)]
    weight: Annotated[float, Field(..., gt = 0, description="The weight of the patient in kilograms", example=70.5)]

    @computed_field
    @property
    def bmi(self) -> float: 
        return round(self.weight / (self.height ** 2), 2)
    
    @computed_field
    @property
    def verdict(self) -> str:
        bmi_value = self.bmi
        if bmi_value < 18.5:
            return "Underweight"
        elif 18.5 <= bmi_value < 24.9:
            return "Normal weight"
        elif 25 <= bmi_value < 29.9:
            return "Overweight"
        else:
            return "Obese"


def load_data():
    with open("patients.json", "r") as file:
        data =  json.load(file)
    return data

def save_data(data):
    with open("patients.json", "w") as file:
        json.dump(data, file)

@app.get("/")
def hello():
    return {"message": "Patient Management System API"}

@app.get("/about")
def about():
    return {"message": "A fully functional Patient Management System API."}

@app.get("/view")
def view():
    data = load_data()

    return data


@app.get("/patient/{patient_id}")
def view_patient(patient_id: str = Path(..., description="The ID of the patient to retrieve", example = "P001")):
    data = load_data()

    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail="Patient not found.")

@app.get("/sort")
def sort_patients(sort_by: str = Query(..., description="sort on the basis of height, weight or bmi"), order: str = Query('asc', description="sort order, either 'asc' for ascending or 'desc' for descending")):
    valid_fields = ['height', 'weight', 'bmi']

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f"Invalid field select from {valid_fields}")

    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail="Invalid order, select between 'asc' or 'desc'")

    data = load_data()

    sorted_data = sorted(data.values(), key=lambda x: x.get(sort_by, 0), reverse=(order == 'desc'))

    return sorted_data

@app.post("/create")
def create_patient(patient: Patient):
    data = load_data()

    if patient.id in data:
        raise HTTPException(status_code=400, detail="Patient with this ID already exists.")

    data[patient.id] = patient.model_dump(exclude = ["id"])

    save_data(data)

    return JSONResponse(status_code=201, content={"message": "Patient created successfully."})
