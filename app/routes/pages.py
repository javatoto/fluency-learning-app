"""
Page routes for rendering HTML templates.
"""
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.topic import Topic
from typing import Optional

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="app/templates")


def get_current_user_optional(request: Request, db: Session = Depends(get_db)):
    """Get current user from session if logged in, otherwise None."""
    user_id = request.session.get("user_id")
    if not user_id:
        return None

    from app.models.user import User
    user = db.query(User).filter(User.id == user_id).first()
    return user


@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    """Home page with topic selection."""
    user = get_current_user_optional(request, db)
    topics = db.query(Topic).all()

    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "user": user,
            "topics": topics
        }
    )


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page."""
    return templates.TemplateResponse(
        "login.html",
        {"request": request}
    )


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Registration page."""
    return templates.TemplateResponse(
        "register.html",
        {"request": request}
    )


@router.get("/logout")
async def logout_page(request: Request):
    """Logout and redirect to homepage."""
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)


@router.get("/practice", response_class=HTMLResponse)
async def practice_page(request: Request, topic: int = None, db: Session = Depends(get_db)):
    """Practice page for pronunciation exercises."""
    if not topic:
        return RedirectResponse(url="/", status_code=303)

    user = get_current_user_optional(request, db)
    topic_obj = db.query(Topic).filter(Topic.id == topic).first()

    if not topic_obj:
        return RedirectResponse(url="/", status_code=303)

    return templates.TemplateResponse(
        "practice.html",
        {
            "request": request,
            "user": user,
            "topic": topic_obj
        }
    )


@router.get("/progress", response_class=HTMLResponse)
async def progress_page(request: Request, db: Session = Depends(get_db)):
    """Progress dashboard page."""
    user = get_current_user_optional(request, db)

    if not user:
        return RedirectResponse(url="/login", status_code=303)

    return templates.TemplateResponse(
        "progress.html",
        {
            "request": request,
            "user": user
        }
    )
