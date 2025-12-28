"""Grade data access layer."""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.grade import Grade
from app.schemas.grade import GradeCreate


async def add_grade(
    session: AsyncSession,
    grade_data: GradeCreate,
) -> Grade:
    """Add a grade for a student."""
    grade = Grade(
        id=uuid.uuid4(),
        student_id=grade_data.student_id,
        score=grade_data.score,
    )
    session.add(grade)
    await session.commit()
    await session.refresh(grade)
    return grade

