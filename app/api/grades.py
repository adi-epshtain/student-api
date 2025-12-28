"""Grade API routes."""
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.grade import GradeCreate, GradeCreateBody, GradeResponse
from app.services.grade import add_grade

router = APIRouter(prefix="/students", tags=["grades"])


@router.post("/{student_id}/grades", response_model=GradeResponse, status_code=201)
async def create_grade(
    student_id: uuid.UUID,
    grade_data: GradeCreateBody,
    db: AsyncSession = Depends(get_db),
) -> GradeResponse:
    """Add a grade for a student."""
    # Create grade data with student_id from path parameter
    grade_create = GradeCreate(
        student_id=student_id,
        score=grade_data.score,
    )
    
    try:
        return await add_grade(db, grade_create)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

