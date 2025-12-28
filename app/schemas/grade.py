"""Grade Pydantic schemas."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class GradeCreate(BaseModel):
    """Schema for creating a grade."""
    
    student_id: uuid.UUID = Field(..., description="Student ID")
    score: int = Field(..., ge=0, le=100, description="Grade score (0-100)")


class GradeCreateBody(BaseModel):
    """Schema for grade creation request body (score only)."""
    
    score: int = Field(..., ge=0, le=100, description="Grade score (0-100)")


class GradeResponse(BaseModel):
    """Schema for grade response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    student_id: uuid.UUID
    score: int
    created_at: datetime

