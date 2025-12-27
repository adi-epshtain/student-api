"""Grade Pydantic schemas."""
import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class GradeCreate(BaseModel):
    """Schema for creating a grade."""
    
    student_id: uuid.UUID = Field(..., description="Student ID")
    score: int = Field(..., ge=0, le=100, description="Grade score (0-100)")


class GradeResponse(BaseModel):
    """Schema for grade response."""
    
    id: uuid.UUID
    student_id: uuid.UUID
    score: int
    created_at: datetime
    
    class Config:
        from_attributes = True

