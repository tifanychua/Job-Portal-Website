from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.sessions import SessionMiddleware


# ==================================================
# Import Routers
# ==================================================

# Interview router
from src.job_portal_web.backend.interview import (
    router as interview_router
)

# Applicant router
from src.job_portal_web.backend.applicant import (
    router as applicant_router
)

# Employer job management router
from src.job_portal_web.backend.routes.employer import (
    router as employer_router
)

# Employer application management router
from src.job_portal_web.backend.routes.employerApplication import (
    router as employer_application_router
)


# ==================================================
# Create FastAPI Application
# ==================================================

app = FastAPI()


# ==================================================
# Session Middleware
# ==================================================

app.add_middleware(
    SessionMiddleware,
    secret_key="agileAsg"
)


# ==================================================
# Register Routers
# ==================================================

app.include_router(interview_router)

app.include_router(applicant_router)

app.include_router(employer_router)

app.include_router(employer_application_router)


# ==================================================
# Base Folders
# ==================================================

# Points to:
# src/job_portal_web/

BASE_DIR = Path(__file__).resolve().parent.parent


# Points to:
# src/job_portal_web/ui/

UI_DIR = BASE_DIR / "ui"


# ==================================================
# Mount Static Files
# ==================================================

# CSS files:
# http://127.0.0.1:8000/css/filename.css

app.mount(
    "/css",
    StaticFiles(
        directory=str(BASE_DIR / "css")
    ),
    name="css"
)


# Image files:
# http://127.0.0.1:8000/images/filename.png

app.mount(
    "/images",
    StaticFiles(
        directory=str(BASE_DIR / "images")
    ),
    name="images"
)


# Other static files

app.mount(
    "/static",
    StaticFiles(
        directory=str(UI_DIR)
    ),
    name="static"
)


# ==================================================
# Home Page
# ==================================================

@app.get("/")
def home():

    return FileResponse(
        str(
            UI_DIR / "home.html"
        )
    )


# ==================================================
# Login Page
# ==================================================

@app.get("/login")
def login_page():

    return FileResponse(
        str(
            UI_DIR / "login.html"
        )
    )


# ==================================================
# Interview Schedule Page
# ==================================================

@app.get("/interview_schedule")
def schedule_page():

    return FileResponse(
        str(
            UI_DIR /
            "interview_schedule.html"
        )
    )


# ==================================================
# Schedule List Page
# ==================================================

@app.get("/schedule_list")
def schedule_list_page():

    return FileResponse(
        str(
            UI_DIR /
            "schedule_list.html"
        )
    )


# ==================================================
# Applicants Page
# ==================================================

@app.get("/applicants")
def applicants_page():

    return FileResponse(
        str(
            UI_DIR /
            "applicants.html"
        )
    )