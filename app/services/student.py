"""Student service layer."""
from typing import Literal

from sqlalchemy.ext.asyncio import AsyncSession

from app.dal.student import create_student as dal_create_student, list_students_with_avg as dal_list_students_with_avg
from app.schemas.student import StudentCreate, StudentResponse


async def create_student(
    session: AsyncSession,
    student_data: StudentCreate,
) -> StudentResponse:
    """Create a new student."""
    student = await dal_create_student(session, student_data)
    return StudentResponse.model_validate(student)


async def list_students_with_avg(
    session: AsyncSession,
    min_avg_grade: float | None = None,
    sort_by: Literal["name", "avg_grade", "created_at"] = "name",
    order: Literal["asc", "desc"] = "asc",
    limit: int = 100,
    offset: int = 0,
) -> list[StudentResponse]:
    """
    List students with their average grades.
    
    Business logic:
    - If min_avg_grade is provided, exclude students without grades (NULL avg_grade)
    - This is handled at SQL level via HAVING clause
    """
    # DAL handles SQL aggregation and filtering
    results = await dal_list_students_with_avg(
        session=session,
        min_avg_grade=min_avg_grade,
        sort_by=sort_by,
        order=order,
        limit=limit,
        offset=offset,
    )
    
    # Convert to response schemas
    return [
        StudentResponse(
            id=student.id,
            name=student.name,
            created_at=student.created_at,
            avg_grade=avg_grade,
        )
        for student, avg_grade in results
    ]

