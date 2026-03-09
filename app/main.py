"""
Main FastAPI application setup.
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.config import settings
from app.routes import auth, pages, content, recordings, progress
import os

# Create FastAPI app
app = FastAPI(
    title="Fluency Learning App",
    description="AI-powered English pronunciation learning platform",
    version="1.0.0"
)

# Add session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    max_age=86400 * 7  # 7 days
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
if os.path.exists("app/static"):
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Mount audio files
if os.path.exists("audio_files"):
    app.mount("/audio", StaticFiles(directory="audio_files"), name="audio")

# Register routers
app.include_router(auth.router)
app.include_router(content.router)
app.include_router(recordings.router)
app.include_router(progress.router)
app.include_router(pages.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Fluency Learning App API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Error handlers
templates = Jinja2Templates(directory="app/templates")


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions with custom error pages."""
    # For API routes, return JSON
    if request.url.path.startswith("/api/"):
        return {"detail": exc.detail, "status_code": exc.status_code}

    # For page routes, return HTML error page
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "status_code": exc.status_code,
            "message": exc.detail,
            "detail": None
        },
        status_code=exc.status_code
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    # Log the error (in production, use proper logging)
    print(f"Unexpected error: {exc}")

    # For API routes, return JSON
    if request.url.path.startswith("/api/"):
        return {"detail": "Internal server error", "status_code": 500}

    # For page routes, return HTML error page
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "status_code": 500,
            "message": "An unexpected error occurred",
            "detail": str(exc) if settings.DEBUG else None
        },
        status_code=500
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
