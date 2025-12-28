"""Grade service layer."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.dal.grade import add_grade as dal_add_grade
from app.models.student import Student
from app.schemas.grade import GradeCreate, GradeResponse


async def add_grade(
    session: AsyncSession,
    grade_data: GradeCreate,
) -> GradeResponse:
    """
    Add a grade for a student.
    
    Validates student exists before adding grade.
    """
    # Validate student exists
    stmt = select(Student).where(Student.id == grade_data.student_id)
    result = await session.execute(stmt)
    student = result.scalar_one_or_none()
    
    if student is None:
        raise ValueError(f"Student with id {grade_data.student_id} not found")
    
    # Create grade via DAL
    grade = await dal_add_grade(session, grade_data)
    return GradeResponse.model_validate(grade)

