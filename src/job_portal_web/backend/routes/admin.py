
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
import os

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UI_DIR = os.path.join(BASE_DIR, "ui")
templates = Jinja2Templates(directory=UI_DIR)


@router.get("/admin/dashboard")
def admin_dashboard(request: Request):
    admin_id = request.session.get("admin_id")

    if not admin_id:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/login?role=admin", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="admin_dashboard.html",
        context={"active_page": "admin"},
    )
