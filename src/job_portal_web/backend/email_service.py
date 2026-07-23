from fastapi_mail import FastMail, MessageSchema, MessageType
from .email_config import conf


async def send_interview_email(email, name, interview, company_address):

    location_text = ""

    if interview.interviewType == "online":

        location_text = f"""
Meeting Link:
{interview.meetingLink}
"""

    elif interview.interviewType == "physical":

        location_text = f"""
Company Address:
{company_address}
"""

    message = MessageSchema(
        subject="Interview Scheduled - JobConnect",
        recipients=[email],
        body=f"""

Dear {name},

Your interview has been scheduled.

Interview Stage:
{interview.stage}

Date:
{interview.date}

Time:
{interview.time}

Duration:
{interview.duration}

Interview Type:
{interview.interviewType}

{location_text}

Regards,
JobConnect Team

""",
        subtype=MessageType.plain,
    )

    fm = FastMail(conf)

    await fm.send_message(message)


async def send_employer_interview_notification(
    email,
    employer_name,
    candidate_name,
    position,
    status,
    reason=None,
    requested_date=None,
    requested_time=None,
):

    reschedule_text = ""

    if status == "Reschedule Requested":

        reschedule_text = f"""

Requested New Interview Date:
{requested_date}


Requested New Interview Time:
{requested_time}

"""

    reason_text = ""

    if reason:

        reason_text = f"""

Reason:
{reason}

"""

    message = MessageSchema(
        subject=f"Interview Update - {status}",
        recipients=[email],
        body=f"""

Dear {employer_name},


The interview status has been updated by the candidate.


Candidate:
{candidate_name}


Position:
{position}


Status:
{status}


{reschedule_text}


{reason_text}


Please login to JobConnect to view the interview details.


Regards,

JobConnect Team

""",
        subtype=MessageType.plain,
    )

    fm = FastMail(conf)

    await fm.send_message(message)


async def send_password_reset_email(email, name, reset_link):
    """
    NEW: sends a password-reset link. Used by backend/auth.py's
    /forgot-password route. Link expires in 30 minutes (see
    RESET_TOKEN_TTL_MINUTES in auth.py).
    """

    message = MessageSchema(
        subject="Reset Your Password - JobConnect",
        recipients=[email],
        body=f"""

Dear {name},

We received a request to reset your JobConnect password.

Click the link below to choose a new password. This link expires in 30 minutes:

{reset_link}

If you did not request this, you can safely ignore this email — your password will not be changed.

Regards,
JobConnect Team

""",
        subtype=MessageType.plain,
    )

    fm = FastMail(conf)

    await fm.send_message(message)
