"""Main application entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api import grades_router, students_router
from app.core.config import settings
from app.core.database import init_db
from app.models import Grade, Student  # noqa: F401 - Import to register models


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup: initialize database
    await init_db()
    yield
    # Shutdown: cleanup if needed
    pass


app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    lifespan=lifespan,
)

# Register routers
app.include_router(students_router)
app.include_router(grades_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Students Grades API"}

