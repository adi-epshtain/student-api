"""Student API routes."""
from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.student import StudentCreate, StudentResponse
from app.services.student import create_student, list_students_with_avg

router = APIRouter(prefix="/students", tags=["students"])


@router.post("", response_model=StudentResponse, status_code=201)
async def create_student_endpoint(
    student_data: StudentCreate,
    db: AsyncSession = Depends(get_db),
) -> StudentResponse:
    """Create a new student."""
    return await create_student(db, student_data)


@router.get("", response_model=list[StudentResponse])
async def list_students(
    min_avg_grade: float | None = Query(None, ge=0, le=100, description="Minimum average grade filter"),
    sort_by: Literal["name", "avg_grade", "created_at"] = Query("name", description="Field to sort by"),
    order: Literal["asc", "desc"] = Query("asc", description="Sort order"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: AsyncSession = Depends(get_db),
) -> list[StudentResponse]:
    """List students with their average grades."""
    return await list_students_with_avg(
        session=db,
        min_avg_grade=min_avg_grade,
        sort_by=sort_by,
        order=order,
        limit=limit,
        offset=offset,
    )

