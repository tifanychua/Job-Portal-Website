from pathlib import Path
import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.sessions import SessionMiddleware

from src.job_portal_web.backend.interview import router as interview_router
from src.job_portal_web.backend.applicant import router as applicant_router
from src.job_portal_web.backend.routes.employer import router as employer_router


app = FastAPI()

app.include_router(interview_router)
app.include_router(applicant_router)
app.include_router(employer_router)


# Base folders
BASE_DIR = Path(__file__).resolve().parent.parent
UI_DIR = BASE_DIR / "ui"


# Mount static files
app.mount("/css", StaticFiles(directory=str(BASE_DIR / "css")), name="css")
app.mount("/images", StaticFiles(directory=str(BASE_DIR / "images")), name="images")
app.mount("/static", StaticFiles(directory=str(UI_DIR)), name="static")


@app.get("/")
def home():
    return FileResponse(str(UI_DIR / "home.html"))


@app.get("/login")
def login_page():
    return FileResponse(str(UI_DIR / "login.html"))


@app.get("/interview_schedule")
def schedule_page():
    return FileResponse(str(UI_DIR / "interview_schedule.html"))


@app.get("/schedule_list")
def schedule_list_page():
    return FileResponse(str(UI_DIR / "schedule_list.html"))


@app.get("/applicants")
def applicants_page():
    return FileResponse(str(UI_DIR / "applicants.html"))


app.add_middleware(
    SessionMiddleware,
    secret_key="agileAsg"
)