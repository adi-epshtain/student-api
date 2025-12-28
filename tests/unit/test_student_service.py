"""Unit tests for student service layer."""
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

from app.models.student import Student
from app.schemas.student import StudentCreate, StudentResponse
from app.services.student import create_student, list_students_with_avg


@pytest.mark.asyncio
async def test_create_student_converts_to_response_schema():
    """Test that create_student converts DAL result to StudentResponse."""
    # Mock data
    student_id = uuid.uuid4()
    student_name = "Alice"
    created_at = datetime.now()
    
    mock_student = Student(
        id=student_id,
        name=student_name,
        created_at=created_at,
    )
    
    student_data = StudentCreate(name=student_name)
    mock_session = AsyncMock()
    
    # Mock DAL function
    with patch("app.services.student.dal_create_student", new_callable=AsyncMock) as mock_dal:
        mock_dal.return_value = mock_student
        
        # Call service
        result = await create_student(mock_session, student_data)
        
        # Verify DAL was called
        mock_dal.assert_called_once_with(mock_session, student_data)
        
        # Verify response schema
        assert isinstance(result, StudentResponse)
        assert result.id == student_id
        assert result.name == student_name
        assert result.created_at == created_at


@pytest.mark.asyncio
async def test_list_students_with_avg_converts_tuples_to_responses():
    """Test that list_students_with_avg converts DAL tuples to StudentResponse."""
    # Mock data
    student1_id = uuid.uuid4()
    student2_id = uuid.uuid4()
    student3_id = uuid.uuid4()
    
    student1 = Student(id=student1_id, name="Alice", created_at=datetime.now())
    student2 = Student(id=student2_id, name="Bob", created_at=datetime.now())
    student3 = Student(id=student3_id, name="Charlie", created_at=datetime.now())
    
    # DAL returns tuples: (Student, avg_grade)
    mock_results = [
        (student1, 90.0),
        (student2, 75.5),
        (student3, None),  # Student without grades
    ]
    
    mock_session = AsyncMock()
    
    # Mock DAL function
    with patch("app.services.student.dal_list_students_with_avg", new_callable=AsyncMock) as mock_dal:
        mock_dal.return_value = mock_results
        
        # Call service
        results = await list_students_with_avg(
            session=mock_session,
            min_avg_grade=None,
            sort_by="name",
            order="asc",
            limit=100,
            offset=0,
        )
        
        # Verify DAL was called with correct parameters
        mock_dal.assert_called_once_with(
            session=mock_session,
            min_avg_grade=None,
            sort_by="name",
            order="asc",
            limit=100,
            offset=0,
        )
        
        # Verify response schemas
        assert len(results) == 3
        assert all(isinstance(r, StudentResponse) for r in results)
        
        # Verify data transformation
        assert results[0].id == student1_id
        assert results[0].name == "Alice"
        assert results[0].avg_grade == 90.0
        
        assert results[1].id == student2_id
        assert results[1].name == "Bob"
        assert results[1].avg_grade == 75.5
        
        assert results[2].id == student3_id
        assert results[2].name == "Charlie"
        assert results[2].avg_grade is None  # Student without grades


@pytest.mark.asyncio
async def test_list_students_with_avg_passes_min_avg_grade_to_dal():
    """Test that min_avg_grade parameter is passed to DAL."""
    mock_session = AsyncMock()
    mock_dal_results = []
    
    with patch("app.services.student.dal_list_students_with_avg", new_callable=AsyncMock) as mock_dal:
        mock_dal.return_value = mock_dal_results
        
        # Call with min_avg_grade
        await list_students_with_avg(
            session=mock_session,
            min_avg_grade=85.0,
            sort_by="avg_grade",
            order="desc",
            limit=50,
            offset=10,
        )
        
        # Verify DAL was called with min_avg_grade
        mock_dal.assert_called_once_with(
            session=mock_session,
            min_avg_grade=85.0,
            sort_by="avg_grade",
            order="desc",
            limit=50,
            offset=10,
        )


@pytest.mark.asyncio
async def test_list_students_with_avg_handles_empty_results():
    """Test that list_students_with_avg handles empty DAL results."""
    mock_session = AsyncMock()
    
    with patch("app.services.student.dal_list_students_with_avg", new_callable=AsyncMock) as mock_dal:
        mock_dal.return_value = []
        
        results = await list_students_with_avg(mock_session)
        
        assert results == []
        mock_dal.assert_called_once()

