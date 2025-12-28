"""API routes."""
from app.api.grades import router as grades_router
from app.api.students import router as students_router

__all__ = ["students_router", "grades_router"]

