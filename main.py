from fastapi import FastAPI, Path, HTTPException, Query
import json

app = FastAPI()

def load_data():
    with open("patients.json", "r") as file:
        data =  json.load(file)
    return data

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