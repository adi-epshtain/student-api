"""Pydantic schemas."""
from app.schemas.grade import GradeCreate, GradeCreateBody, GradeResponse
from app.schemas.student import StudentCreate, StudentResponse

__all__ = [
    "StudentCreate",
    "StudentResponse",
    "GradeCreate",
    "GradeCreateBody",
    "GradeResponse",
]

