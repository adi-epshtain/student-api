"""Grade data access layer."""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.grade import Grade
from app.models.student import Student
from app.schemas.grade import GradeCreate


async def add_grade(
    session: AsyncSession,
    grade_data: GradeCreate,
) -> Grade:
    """Add a grade for a student."""
    # Verify student exists
    stmt = select(Student).where(Student.id == grade_data.student_id)
    result = await session.execute(stmt)
    student = result.scalar_one_or_none()
    
    if student is None:
        raise ValueError(f"Student with id {grade_data.student_id} not found")
    
    grade = Grade(
        id=uuid.uuid4(),
        student_id=grade_data.student_id,
        score=grade_data.score,
    )
    session.add(grade)
    await session.commit()
    await session.refresh(grade)
    return grade

