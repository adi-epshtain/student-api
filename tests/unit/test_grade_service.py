"""Unit tests for grade service layer."""
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.grade import Grade
from app.models.student import Student
from app.schemas.grade import GradeCreate, GradeResponse
from app.services.grade import add_grade


@pytest.mark.asyncio
async def test_add_grade_validates_student_exists():
    """Test that add_grade validates student exists before adding grade."""
    student_id = uuid.uuid4()
    grade_data = GradeCreate(student_id=student_id, score=85)
    
    mock_student = Student(id=student_id, name="Alice", created_at=datetime.now())
    mock_grade = Grade(
        id=uuid.uuid4(),
        student_id=student_id,
        score=85,
        created_at=datetime.now(),
    )
    
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_student
    mock_session.execute.return_value = mock_result
    
    # Mock DAL function
    with patch("app.services.grade.dal_add_grade", new_callable=AsyncMock) as mock_dal:
        mock_dal.return_value = mock_grade
        
        # Call service
        result = await add_grade(mock_session, grade_data)
        
        # Verify student validation query was executed
        mock_session.execute.assert_called_once()
        
        # Verify DAL was called
        mock_dal.assert_called_once_with(mock_session, grade_data)
        
        # Verify response schema
        assert isinstance(result, GradeResponse)
        assert result.student_id == student_id
        assert result.score == 85


@pytest.mark.asyncio
async def test_add_grade_raises_value_error_when_student_not_found():
    """Test that add_grade raises ValueError when student doesn't exist."""
    student_id = uuid.uuid4()
    grade_data = GradeCreate(student_id=student_id, score=85)
    
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None  # Student not found
    mock_session.execute.return_value = mock_result
    
    # Mock DAL function
    with patch("app.services.grade.dal_add_grade", new_callable=AsyncMock) as mock_dal:
        # Call service - should raise ValueError
        with pytest.raises(ValueError, match=f"Student with id {student_id} not found"):
            await add_grade(mock_session, grade_data)
        
        # Verify DAL was NOT called (validation failed before grade creation)
        mock_dal.assert_not_called()


@pytest.mark.asyncio
async def test_add_grade_converts_dal_result_to_response_schema():
    """Test that add_grade converts DAL result to GradeResponse."""
    student_id = uuid.uuid4()
    grade_id = uuid.uuid4()
    grade_data = GradeCreate(student_id=student_id, score=90)
    
    mock_student = Student(id=student_id, name="Bob", created_at=datetime.now())
    mock_grade = Grade(
        id=grade_id,
        student_id=student_id,
        score=90,
        created_at=datetime.now(),
    )
    
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_student
    mock_session.execute.return_value = mock_result
    
    with patch("app.services.grade.dal_add_grade", new_callable=AsyncMock) as mock_dal:
        mock_dal.return_value = mock_grade
        
        result = await add_grade(mock_session, grade_data)
        
        # Verify response schema
        assert isinstance(result, GradeResponse)
        assert result.id == grade_id
        assert result.student_id == student_id
        assert result.score == 90


@pytest.mark.asyncio
async def test_add_grade_business_rule_student_validation_before_grade_creation():
    """Test business rule: student validation happens before grade creation."""
    student_id = uuid.uuid4()
    grade_data = GradeCreate(student_id=student_id, score=75)
    
    mock_student = Student(id=student_id, name="Charlie", created_at=datetime.now())
    mock_grade = Grade(
        id=uuid.uuid4(),
        student_id=student_id,
        score=75,
        created_at=datetime.now(),
    )
    
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_student
    
    call_order = []
    
    # Track call order using side_effect
    async def tracked_execute(*args, **kwargs):
        call_order.append("validate_student")
        return mock_result
    
    mock_session.execute = AsyncMock(side_effect=tracked_execute)
    
    with patch("app.services.grade.dal_add_grade", new_callable=AsyncMock) as mock_dal:
        async def tracked_dal(*args, **kwargs):
            call_order.append("create_grade")
            return mock_grade
        
        mock_dal.side_effect = tracked_dal
        
        await add_grade(mock_session, grade_data)
        
        # Verify validation happens before grade creation
        assert call_order == ["validate_student", "create_grade"]

