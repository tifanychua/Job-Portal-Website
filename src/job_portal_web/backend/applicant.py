from fastapi import APIRouter
from src.job_portal_web.backend.database import db

router = APIRouter()


# Get all shortlisted applicants
@router.get("/api/applicants/shortlisted")
def get_shortlisted_candidates():

    applicants = []

    docs = db.collection("applicants").where("status", "==", "Shortlisted").stream()

    for doc in docs:

        data = doc.to_dict()

        data["id"] = doc.id

        # Retrieve skills from skills collection

        skills = []

        skill_docs = db.collection("skills").where("applicantId", "==", doc.id).stream()

        for skill_doc in skill_docs:

            skill = skill_doc.to_dict()

            skills.append({"name": skill.get("skillName"), "category": skill.get("category")})

        data["skills"] = skills

        applicants.append(data)

    return applicants


# Get one shortlisted applicant
@router.get("/api/applicants/shortlisted/{id}")
def get_single_candidate(id: str):

    doc = db.collection("applicants").document(id).get()

    if not doc.exists:

        return {"error": "Applicant not found"}

    data = doc.to_dict()

    data["id"] = id

    skills = []

    skill_docs = db.collection("skills").where("applicantId", "==", id).stream()

    for skill_doc in skill_docs:

        skill = skill_doc.to_dict()

        skills.append({"name": skill.get("skillName"), "category": skill.get("category")})

    data["skills"] = skills

    return data
