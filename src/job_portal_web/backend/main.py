from fastapi import FastAPI
from fastapi.responses import FileResponse
import os

app = FastAPI()

UI_DIR = "/home/user/Job Portal Web/src/job_portal_web/ui"

@app.get("/")
async def home():
    return FileResponse(os.path.join(UI_DIR, "home.html"))

@app.get("/login")
async def login_page():
    return FileResponse(os.path.join(UI_DIR, "login.html"))