from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from job_portal_web.backend.routes.employer import router as employer_router

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key="agileAsg"
)

BASE_DIR = Path(__file__).resolve().parent.parent

app.mount("/css", StaticFiles(directory=str(BASE_DIR / "css")), name="css")
app.mount("/images", StaticFiles(directory=str(BASE_DIR / "images")), name="images")

app.include_router(employer_router)