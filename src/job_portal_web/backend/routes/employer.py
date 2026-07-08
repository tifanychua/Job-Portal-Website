from pathlib import Path
from typing import List
from datetime import datetime
import uuid

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from firebase_admin import firestore
from job_portal_web.backend.firebase_config import db

router = APIRouter()

# Project root (job_portal_web)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

templates = Jinja2Templates(
    directory=str(BASE_DIR / "ui")
)


# ==================================================
# Manage Jobs
# ==================================================

@router.get("/manage-jobs", response_class=HTMLResponse)
async def manage_jobs(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="jobPosted.html",
        context={
            "request": request
        }
    )


# ==================================================
# Publish Job Page
# ==================================================

@router.get("/publish-job", response_class=HTMLResponse)
async def publish_job(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="publishJob.html",
        context={
            "request": request
        }
    )


# ==================================================
# Save Form -> Session -> Preview
# ==================================================

@router.post("/review-job", response_class=HTMLResponse)
async def review_job(

    request: Request,

    # ---------- Job Information ----------

    job_title: str = Form(...),
    category: str = Form(...),
    employment_type: str = Form(...),
    position: str = Form(...),
    vacancies: int = Form(...),
    location: str = Form(...),

    # ---------- Job Details ----------

    job_desc: str = Form(...),
    job_responsibility: str = Form(...),
    job_req: str = Form(...),
    additional_info: str = Form(""),

    # ---------- Salary ----------

    salaryType: str = Form(...),
    salary: str = Form(""),
    minSalary: str = Form(""),
    maxSalary: str = Form(""),

    # ---------- Benefits ----------

    benefits: List[str] = Form([]),
    other_benefit: str = Form("")

):

    # Add Other Benefit
    if other_benefit.strip():
        benefits.append(other_benefit.strip())

    # Create salary display
    if salaryType == "fixed":
        salary_display = f"RM {salary}"

    elif salaryType == "range":
        salary_display = f"RM {minSalary} - RM {maxSalary}"

    else:
        salary_display = "Negotiable"

    # Save to Session
    request.session["job"] = {

        "job_title": job_title,
        "category": category,
        "employment_type": employment_type,
        "position": position,
        "vacancies": vacancies,
        "location": location,

        "job_desc": job_desc,
        "job_responsibility": job_responsibility,
        "job_req": job_req,
        "additional_info": additional_info,

        "salaryType": salaryType,
        "salary": salary,
        "minSalary": minSalary,
        "maxSalary": maxSalary,
        "salary_display": salary_display,

        "benefits": benefits

    }

    print(request.session["job"])

    return templates.TemplateResponse(
        request=request,
        name="reviewJob.html",
        context={
            "request": request,
            "job": request.session["job"]
        }
    )


# ==================================================
# Review Page
# ==================================================

@router.get("/review-job", response_class=HTMLResponse)
async def review_page(request: Request):

    job = request.session.get("job")

    return templates.TemplateResponse(
        request=request,
        name="reviewJob.html",
        context={
            "request": request,
            "job": job
        }
    )

def generate_job_id():

    today = datetime.now().strftime("%y%m%d")

    prefix = f"JL{today}"

    docs = (
        db.collection("job_list")
        .where("job_id", ">=", prefix)
        .where("job_id", "<=", prefix + "\uf8ff")
        .stream()
    )

    count = sum(1 for _ in docs)

    running_no = f"{count + 1:04d}"

    return prefix + running_no

@router.post("/publish-job-confirm")
async def publish_job_confirm(request: Request):

    job = request.session.get("job")

    if not job:
        return RedirectResponse(
            url="/publish-job",
            status_code=303
        )

    # Generate Job ID
    job_id = generate_job_id()

    # Additional fields
    job["job_id"] = job_id
    job["status"] = "Active"
    job["created_at"] = firestore.SERVER_TIMESTAMP
    job["updated_at"] = firestore.SERVER_TIMESTAMP

    # Save to Firestore
    db.collection("job_list").document(job_id).set(job)

    # Remove temporary session
    request.session.pop("job", None)

    return RedirectResponse(
        url="/manage-jobs",
        status_code=303
    )