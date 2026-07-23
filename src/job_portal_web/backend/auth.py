

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Request, Form
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from .database import db
from firebase_admin import auth, firestore
from google.cloud.firestore_v1 import SERVER_TIMESTAMP
from pydantic import BaseModel

import os

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UI_DIR = os.path.join(BASE_DIR, "ui")
templates = Jinja2Templates(directory=UI_DIR)


# Roles that are allowed to self-register / use forgot-password.
# Admin is deliberately excluded — admin accounts are provisioned manually.
SELF_SERVICE_ROLES = {"job_seeker", "employer"}

# role -> Firestore collection name
ROLE_COLLECTION = {
    "job_seeker": "job_seeker",
    "employer": "company",
    "admin": "admin",
}
class LoginToken(BaseModel):
    token: str

class JobSeekerRegisterRequest(BaseModel):
    token: str
    name: str
    phone: str
   
class EmployerRegisterRequest(BaseModel):
    token: str

    companyName: str
    registrationNumber: str
    businessEmail: str

    phone: str
    industry: str
    companySize: str
    companyWebsite: str
    companyDescription: str

    address: str
    city: str
    state: str
    postalCode: str
    country: str

    contactFullName: str
    contactJobTitle: str
    contactDepartment: str
    contactEmail: str
    contactPhone: str
    altPhone: Optional[str] = ""

    preferredContactMethod: str
    bestTimeToContact: str
    correspondenceAddress: str

   
    
RESET_TOKEN_TTL_MINUTES = 30

ROLE_LABEL = {
    "job_seeker": "Job Seeker",
    "employer": "Employer",
    "admin": "Admin",
}


# ==============================
# Helpers
# ==============================


def _find_user_by_email(collection_name, email):
    """Return (doc_id, data_dict) for the first user with this email, or (None, None)."""
    if not email:
        return None, None

    matches = (
        db.collection(collection_name)
        .where("email", "==", email.strip().lower())
        .limit(1)
        .stream()
    )
    for doc in matches:
        return doc.id, doc.to_dict()

    return None, None


def _now_utc():
    return datetime.now(timezone.utc)


# ==============================
# LOGIN  (job_seeker / employer / admin)
# ==============================


@router.get("/login")
def login_page(request: Request):
    error = request.query_params.get("error")
    reset_success = request.query_params.get("reset") == "success"
    registered = request.query_params.get("registered") == "success"
    role = request.query_params.get("role", "job_seeker")
    if role not in ROLE_LABEL:
        role = "job_seeker"

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "error": error,
            "reset_success": reset_success,
            "registered": registered,
            "role": role,
            "role_label": ROLE_LABEL[role],
        },
    )


@router.post("/firebase-login")
async def firebase_login(
    request: Request,
    data: LoginToken
):

    try:

        decoded = auth.verify_id_token(data.token)

        uid = decoded["uid"]

    except Exception:

        return JSONResponse(
            {"error": "Invalid Token"},
            status_code=401
        )

    job = db.collection("job_seeker").document(uid).get()

    if job.exists:

        request.session["user_type"] = "job_seeker"

        request.session["applicant_id"] = uid

        return {
            "redirect": "/"
        }

    company = db.collection("company").document(uid).get()

    if company.exists:

        request.session["user_type"] = "employer"

        request.session["company_id"] = uid

        return {
            "redirect": "/manage-jobs"
        }

    admin = db.collection("admin").document(uid).get()

    if admin.exists:

        request.session["user_type"] = "admin"

        request.session["admin_id"] = uid

        return {
            "redirect": "/admin/dashboard"
        }

    return JSONResponse(
        {"error": "User not found"},
        status_code=401
    )


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)


# ==============================
# REGISTER  (job_seeker / employer only — NOT admin)
# ==============================


@router.get("/register")
def register_page(request: Request):
    error = request.query_params.get("error")
    default_role = request.query_params.get("role", "job_seeker")

    # Employer registration is now its own multi-step wizard.
    if default_role == "employer":
        return RedirectResponse(url="/register/employer", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={"error": error, "default_role": default_role},
    )


@router.post("/firebase-register/job-seeker")
async def firebase_register_job_seeker(
    data: JobSeekerRegisterRequest
):

    try:

        decoded = auth.verify_id_token(data.token)

        uid = decoded["uid"]
        email = decoded["email"]

        db.collection("job_seeker").document(uid).set({

            "uid": uid,

            "name": data.name,

            "email": email,

            "phone": data.phone,

            "profileImage": "user.png",

            "status": "Active",

            "createdAt": firestore.SERVER_TIMESTAMP

        })

        return {
            "success": True
        }

    except Exception as e:

        return JSONResponse(
            status_code=401,
            content={
                "error": str(e)
            }
        )

@router.post("/firebase-register/employer")
async def firebase_register_employer(
    data: EmployerRegisterRequest
):

    try:

        decoded = auth.verify_id_token(data.token)

        uid = decoded["uid"]

        email = decoded["email"]

        company_data = {

            "uid": uid,

            "email": email,

            "companyName": data.companyName,

            "registrationNumber": data.registrationNumber,

            "businessEmail": data.businessEmail,

            "phone": data.phone,

            "industry": data.industry,

            "companySize": data.companySize,

            "companyWebsite": data.companyWebsite,

            "companyDescription": data.companyDescription,

            "address": data.address,

            "city": data.city,

            "state": data.state,

            "postalCode": data.postalCode,

            "country": data.country,

            "contactPerson": {

                "fullName": data.contactFullName,

                "jobTitle": data.contactJobTitle,

                "department": data.contactDepartment,

                "email": data.contactEmail,

                "phone": data.contactPhone,

                "altPhone": data.altPhone,

                "preferredContactMethod": data.preferredContactMethod,

                "bestTimeToContact": data.bestTimeToContact,

                "correspondenceAddress": data.correspondenceAddress

            },

            "logo": "companyLogo.png",

            "status": "Pending",

            "createdAt": firestore.SERVER_TIMESTAMP

        }

        db.collection("company").document(uid).set(company_data)

        return {

            "success": True

        }

    except Exception as e:

        return JSONResponse(

            status_code=401,

            content={
                "error": str(e)
            }

        )
# ==============================
# FORGOT PASSWORD  (job_seeker / employer only — NOT admin)
# ==============================


@router.get("/forgot-password")
def forgot_password_page(request: Request):
    sent = request.query_params.get("sent") == "1"
    default_role = request.query_params.get("role", "job_seeker")

    return templates.TemplateResponse(
        request=request,
        name="forgot_password.html",
        context={"sent": sent, "default_role": default_role},
    )


@router.post("/forgot-password")
async def forgot_password_submit(
    request: Request,
    role: str = Form(...),
    email: str = Form(...),
):
    if role not in SELF_SERVICE_ROLES:
        return RedirectResponse(url="/forgot-password?error=invalid_role", status_code=303)

    collection_name = ROLE_COLLECTION[role]
    user_id, user = _find_user_by_email(collection_name, email)

    # NOTE: we always show the same "check your email" message whether or not
    # the account exists, so this endpoint can't be used to find out which
    # emails are registered.
    if user_id:
        token = generate_reset_token()
        expiry = (_now_utc() + timedelta(minutes=RESET_TOKEN_TTL_MINUTES)).isoformat()

        db.collection(collection_name).document(user_id).update(
            {"resetToken": token, "resetTokenExpiry": expiry}
        )

        display_name = user.get("name") or user.get("companyName") or "there"
        reset_link = str(request.base_url).rstrip("/") + f"/reset-password?role={role}&token={token}"

        await send_password_reset_email(user.get("email"), display_name, reset_link)

    return RedirectResponse(url=f"/forgot-password?sent=1&role={role}", status_code=303)


# ==============================
# RESET PASSWORD  (job_seeker / employer only — NOT admin)
# ==============================


@router.get("/reset-password")
def reset_password_page(request: Request):
    role = request.query_params.get("role", "")
    token = request.query_params.get("token", "")
    error = request.query_params.get("error")

    valid = False
    if role in SELF_SERVICE_ROLES and token:
        collection_name = ROLE_COLLECTION[role]
        matches = (
            db.collection(collection_name)
            .where("resetToken", "==", token)
            .limit(1)
            .stream()
        )
        for doc in matches:
            data = doc.to_dict()
            expiry = data.get("resetTokenExpiry")
            if expiry and datetime.fromisoformat(expiry) > _now_utc():
                valid = True
            break

    return templates.TemplateResponse(
        request=request,
        name="reset_password.html",
        context={"role": role, "token": token, "valid": valid, "error": error},
    )


@router.post("/reset-password")
def reset_password_submit(
    request: Request,
    role: str = Form(...),
    token: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
):
    if role not in SELF_SERVICE_ROLES:
        return RedirectResponse(url="/login?error=invalid_role", status_code=303)

    if new_password != confirm_password:
        return RedirectResponse(
            url=f"/reset-password?role={role}&token={token}&error=password_mismatch",
            status_code=303,
        )

    if len(new_password) < 8:
        return RedirectResponse(
            url=f"/reset-password?role={role}&token={token}&error=password_too_short",
            status_code=303,
        )

    collection_name = ROLE_COLLECTION[role]

    matches = (
        db.collection(collection_name).where("resetToken", "==", token).limit(1).stream()
    )

    user_id = None
    user = None
    for doc in matches:
        user_id = doc.id
        user = doc.to_dict()
        break

    if not user_id:
        return RedirectResponse(url="/forgot-password?error=invalid_token", status_code=303)

    expiry = user.get("resetTokenExpiry")
    if not expiry or datetime.fromisoformat(expiry) <= _now_utc():
        return RedirectResponse(url="/forgot-password?error=expired_token", status_code=303)

    db.collection(collection_name).document(user_id).update(
        {
            "password": hash_password(new_password),
            "resetToken": None,
            "resetTokenExpiry": None,
        }
    )

    return RedirectResponse(url="/login?reset=success", status_code=303)


# ==============================
# EMPLOYER REGISTRATION WIZARD (4-step: company info / contact person /
# account details / review & submit) — richer data model than the
# simple job-seeker registration above.
# ==============================


@router.get("/register/employer")
def register_employer_page(request: Request):
    error = request.query_params.get("error")
    return templates.TemplateResponse(
        request=request,
        name="employer_registration.html",
        context={"error": error},
    )





@router.post("/register/employer/draft")
async def register_employer_save_draft(request: Request):
    """
    Lightweight draft save for the "Save & Continue Later" button.
    Stores whatever partial data the form has at the time, keyed by
    account email if provided, otherwise a fresh draft is created each
    time (good enough for a first pass — swap in a proper draft_id
    stored in a cookie/localStorage if you want true resume-by-link).
    """
    form = await request.form()
    draft_data = {k: v for k, v in form.multi_items()}
    draft_data["savedAt"] = _now_utc().isoformat()

    key = form.get("accountEmail") or form.get("businessEmail")
    doc_ref = (
        db.collection("company_drafts").document(key)
        if key
        else db.collection("company_drafts").document()
    )
    doc_ref.set(draft_data)

    return {"ok": True}


# ==============================
# NOTE on Admin accounts
# ==============================
#
# Per spec, admin has NO self-registration and NO forgot/reset password —
# admin accounts must be created directly in Firestore. To create one,
# run this once from a Python shell in this project (with your venv active):
#
#     from job_portal_web.backend.database import db
#     from job_portal_web.backend.security import hash_password
#
#     db.collection("admin").document().set({
#         "name": "Super Admin",
#         "email": "admin@jobconnect.com",
#         "password": hash_password("choose-a-strong-password"),
#     })
