"""Grade ORM model."""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Integer, DateTime, ForeignKey, CheckConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.student import Student


class Grade(Base):
    """Grade model."""
    
    __tablename__ = "grades"
    
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
    # Relationships
    student: Mapped["Student"] = relationship(
        "Student",
        back_populates="grades",
    )
    
    __table_args__ = (
        CheckConstraint("score >= 0 AND score <= 100", name="check_score_range"),
    )

