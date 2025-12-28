"""Student Pydantic schemas."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class StudentCreate(BaseModel):
    """Schema for creating a student."""
    
    name: str = Field(..., min_length=1, max_length=100, description="Student name")


class StudentResponse(BaseModel):
    """Schema for student response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    name: str
    created_at: datetime
    avg_grade: float | None = Field(None, description="Average grade (computed elsewhere)")


