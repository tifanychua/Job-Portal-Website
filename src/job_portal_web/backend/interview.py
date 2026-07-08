from fastapi import APIRouter
from pydantic import BaseModel
from database import db

router = APIRouter()


class Interview(BaseModel):

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


@router.post("/api/interviews")
def save_interview(interview: Interview):

    db.collection("interviews").add(interview.dict())

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
            }
        )

    return interviews
