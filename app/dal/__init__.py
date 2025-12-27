"""Data access layer."""
from app.dal.grade import add_grade
from app.dal.student import create_student, list_students_with_avg

__all__ = [
    "create_student",
    "add_grade",
    "list_students_with_avg",
]

