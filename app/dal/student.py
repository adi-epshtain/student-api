"""Student data access layer."""
import uuid
from typing import Literal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.grade import Grade
from app.models.student import Student
from app.schemas.student import StudentCreate


async def create_student(
    session: AsyncSession,
    student_data: StudentCreate,
) -> Student:
    """
    Create a new student.
    
    Note: IntegrityError should be handled at the service/API layer
    with proper rollback.
    """
    student = Student(
        id=uuid.uuid4(),
        name=student_data.name,
    )
    session.add(student)
    await session.commit()
    await session.refresh(student)
    return student


async def list_students_with_avg(
    session: AsyncSession,
    min_avg_grade: float | None = None,
    sort_by: Literal["name", "avg_grade", "created_at"] = "name",
    order: Literal["asc", "desc"] = "asc",
    limit: int = 100,
    offset: int = 0,
) -> list[tuple[Student, float | None]]:
    """
    List students with their average grades using SQL aggregation.
    
    Args:
        session: Database session
        min_avg_grade: Filter by minimum average (excludes students without grades)
        sort_by: Field to sort by (validated via Literal type)
        order: Sort direction (validated via Literal type)
        limit: Maximum results (pagination)
        offset: Skip N results (pagination)
    
    Returns:
        List of tuples: (Student, avg_grade). avg_grade is None for students without grades.
    
    Note:
        Uses LEFT JOIN to include students without grades.
        HAVING clause filters out NULL averages when min_avg_grade is provided.
    """
    # Build aggregation query with LEFT JOIN
    stmt = (
        select(
            Student,
            func.avg(Grade.score).label("avg_grade"),
        )
        .outerjoin(Grade, Student.id == Grade.student_id)
        .group_by(Student.id)
    )
    
    # Apply min_avg_grade filter if provided
    # HAVING clause excludes students without grades (NULL avg_grade)
    if min_avg_grade is not None:
        stmt = stmt.having(func.avg(Grade.score) >= min_avg_grade)
    
    # Apply sorting (validated via Literal type in function signature)
    sort_column = {
        "name": Student.name,
        "avg_grade": func.avg(Grade.score),
        "created_at": Student.created_at,
    }[sort_by]
    
    if order == "desc":
        stmt = stmt.order_by(sort_column.desc())
    else:
        stmt = stmt.order_by(sort_column.asc())
    
    # Apply pagination (limit/offset validated in API layer)
    stmt = stmt.limit(limit).offset(offset)
    
    # Execute query
    result = await session.execute(stmt)
    rows = result.all()
    
    # Convert to list of tuples (Student, avg_grade)
    # Access by index: row[0] = Student, row[1] = avg_grade
    return [
        (row[0], float(row[1]) if row[1] is not None else None)
        for row in rows
    ]

