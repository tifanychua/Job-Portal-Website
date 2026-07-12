from fastapi import APIRouter
from pydantic import BaseModel
from .database import db
from .email_service import send_interview_email

router = APIRouter()


class Interview(BaseModel):
    candidateId: str
    companyId: str
    candidateName: str
    position: str
    stage: str
    date: str
    time: str
    duration: str
    interviewType: str
    interviewer: str
    meetingLink: str
    notes: str
    status: str = "Scheduled"


@router.post("/api/interviews")
async def save_interview(interview: Interview):

    # Save interview
    db.collection("interviews").add(interview.dict())

    # Get applicant
    applicant_doc = db.collection("applicants").document(interview.candidateId).get()

    # Get company
    company_doc = db.collection("company").document(interview.companyId).get()

    if applicant_doc.exists and company_doc.exists:

        applicant = applicant_doc.to_dict()

        company = company_doc.to_dict()

        await send_interview_email(
            applicant.get("email"), applicant.get("name"), interview, company.get("address")
        )

    return {"message": "Interview scheduled successfully!"}


@router.get("/api/interviews")
def get_interviews():

    interviews = []

    docs = db.collection("interviews").stream()

    for doc in docs:

        data = doc.to_dict()

        interviews.append(
            {
                "id": doc.id,
                "candidateName": data.get("candidateName"),
                "position": data.get("position"),
                "stage": data.get("stage"),
                "date": data.get("date"),
                "time": data.get("time"),
                "duration": data.get("duration"),
                "interviewType": data.get("interviewType"),
                "interviewer": data.get("interviewer"),
                "meetingLink": data.get("meetingLink"),
                "notes": data.get("notes"),
                "status": data.get("status", "Scheduled"),
            }
        )

    return interviews


@router.put("/api/interviews/{interview_id}/cancel")
def cancel_interview(interview_id: str):

    db.collection("interviews").document(interview_id).update({"status": "Cancelled"})

    return {"message": "Interview cancelled successfully!"}


class InterviewUpdate(BaseModel):

    stage: str
    date: str
    time: str
    duration: str
    interviewType: str
    interviewer: str
    meetingLink: str
    notes: str
    status: str


@router.get("/api/interviews/{interview_id}")
def get_interview(interview_id: str):

    doc = db.collection("interviews").document(interview_id).get()

    if doc.exists:

        data = doc.to_dict()

        data["id"] = doc.id

        return data

    return {"message": "Interview not found"}


@router.put("/api/interviews/{interview_id}")
def update_interview(interview_id: str, interview: InterviewUpdate):

    db.collection("interviews").document(interview_id).update(
        {
            "stage": interview.stage,
            "date": interview.date,
            "time": interview.time,
            "duration": interview.duration,
            "interviewType": interview.interviewType,
            "interviewer": interview.interviewer,
            "meetingLink": interview.meetingLink,
            "notes": interview.notes,
            "status": interview.status,
        }
    )

    return {"message": "Interview rescheduled successfully!"}
