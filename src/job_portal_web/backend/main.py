from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from interview import router as interview_router
from applicant import router as applicant_router
import os

app = FastAPI()
app.include_router(interview_router)
app.include_router(applicant_router)

# Base UI folder (your frontend)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UI_DIR = os.path.join(BASE_DIR, "ui")

# Mount static files (CSS, images, JS)
app.mount("/static", StaticFiles(directory=UI_DIR), name="static")


@app.get("/")
def home():
    return FileResponse(os.path.join(UI_DIR, "home.html"))


@app.get("/login")
def login_page():
    return FileResponse(os.path.join(UI_DIR, "login.html"))


@app.get("/interview_schedule")
def schedule_page():
    return FileResponse(os.path.join(UI_DIR, "interview_schedule.html"))


@app.get("/schedule_list")
def schedule_list_page():
    return FileResponse(os.path.join(UI_DIR, "schedule_list.html"))


@app.get("/applicants")
def applicants_page():
    return FileResponse(os.path.join(UI_DIR, "applicants.html"))
