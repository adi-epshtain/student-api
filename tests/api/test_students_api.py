"""API tests for student endpoints."""
import uuid
from datetime import datetime

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import get_db
from app.dal.grade import add_grade
from app.dal.student import create_student
from app.schemas.grade import GradeCreate
from app.schemas.student import StudentCreate
from main import app


@pytest.fixture
async def client(db_session):
    """Create test client with database dependency override."""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_student_success(client: AsyncClient, db_session):
    """Test POST /students - happy path."""
    response = await client.post(
        "/students",
        json={"name": "Alice"},
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Alice"
    assert "id" in data
    assert "created_at" in data
    assert uuid.UUID(data["id"])  # Valid UUID


@pytest.mark.asyncio
async def test_create_student_validation_error_empty_name(client: AsyncClient):
    """Test POST /students - validation error (empty name)."""
    response = await client.post(
        "/students",
        json={"name": ""},
    )
    
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_create_student_validation_error_missing_name(client: AsyncClient):
    """Test POST /students - validation error (missing name)."""
    response = await client.post(
        "/students",
        json={},
    )
    
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_create_student_validation_error_name_too_long(client: AsyncClient):
    """Test POST /students - validation error (name too long)."""
    response = await client.post(
        "/students",
        json={"name": "A" * 101},  # Exceeds max_length=100
    )
    
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_list_students_empty(client: AsyncClient):
    """Test GET /students - empty list."""
    response = await client.get("/students")
    
    assert response.status_code == 200
    data = response.json()
    assert data == []


@pytest.mark.asyncio
async def test_list_students_with_data(client: AsyncClient, db_session):
    """Test GET /students - with data."""
    # Create test students
    student1 = await create_student(db_session, StudentCreate(name="Alice"))
    student2 = await create_student(db_session, StudentCreate(name="Bob"))
    
    response = await client.get("/students")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    
    names = {s["name"] for s in data}
    assert "Alice" in names
    assert "Bob" in names


@pytest.mark.asyncio
async def test_list_students_with_avg_grade(client: AsyncClient, db_session):
    """Test GET /students - includes average grades."""
    # Create student and grades
    student = await create_student(db_session, StudentCreate(name="Alice"))
    await add_grade(db_session, GradeCreate(student_id=student.id, score=80))
    await add_grade(db_session, GradeCreate(student_id=student.id, score=90))
    
    response = await client.get("/students")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Alice"
    assert data[0]["avg_grade"] == 85.0  # (80 + 90) / 2


@pytest.mark.asyncio
async def test_list_students_with_filter_min_avg_grade(client: AsyncClient, db_session):
    """Test GET /students - filter by min_avg_grade."""
    # Create students with different averages
    student1 = await create_student(db_session, StudentCreate(name="Alice"))
    student2 = await create_student(db_session, StudentCreate(name="Bob"))
    student3 = await create_student(db_session, StudentCreate(name="Charlie"))
    
    # Alice: avg = 90.0
    await add_grade(db_session, GradeCreate(student_id=student1.id, score=90))
    await add_grade(db_session, GradeCreate(student_id=student1.id, score=90))
    
    # Bob: avg = 75.0
    await add_grade(db_session, GradeCreate(student_id=student2.id, score=75))
    await add_grade(db_session, GradeCreate(student_id=student2.id, score=75))
    
    # Charlie: no grades
    
    # Filter for avg >= 85
    response = await client.get("/students?min_avg_grade=85")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Alice"
    assert data[0]["avg_grade"] == 90.0


@pytest.mark.asyncio
async def test_list_students_with_sorting(client: AsyncClient, db_session):
    """Test GET /students - sorting."""
    # Create students
    student1 = await create_student(db_session, StudentCreate(name="Charlie"))
    student2 = await create_student(db_session, StudentCreate(name="Alice"))
    student3 = await create_student(db_session, StudentCreate(name="Bob"))
    
    # Test sort by name ascending
    response = await client.get("/students?sort_by=name&order=asc")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["name"] == "Alice"
    assert data[1]["name"] == "Bob"
    assert data[2]["name"] == "Charlie"
    
    # Test sort by name descending
    response = await client.get("/students?sort_by=name&order=desc")
    
    assert response.status_code == 200
    data = response.json()
    assert data[0]["name"] == "Charlie"
    assert data[1]["name"] == "Bob"
    assert data[2]["name"] == "Alice"


@pytest.mark.asyncio
async def test_list_students_with_sort_by_avg_grade(client: AsyncClient, db_session):
    """Test GET /students - sort by avg_grade."""
    # Create students with different averages
    student1 = await create_student(db_session, StudentCreate(name="Alice"))
    student2 = await create_student(db_session, StudentCreate(name="Bob"))
    
    # Alice: avg = 90.0
    await add_grade(db_session, GradeCreate(student_id=student1.id, score=90))
    
    # Bob: avg = 75.0
    await add_grade(db_session, GradeCreate(student_id=student2.id, score=75))
    
    # Sort by avg_grade descending
    response = await client.get("/students?sort_by=avg_grade&order=desc")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Alice"
    assert data[0]["avg_grade"] == 90.0
    assert data[1]["name"] == "Bob"
    assert data[1]["avg_grade"] == 75.0


@pytest.mark.asyncio
async def test_list_students_with_pagination(client: AsyncClient, db_session):
    """Test GET /students - pagination."""
    # Create multiple students
    for i in range(5):
        await create_student(db_session, StudentCreate(name=f"Student{i}"))
    
    # Test limit
    response = await client.get("/students?limit=2")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    
    # Test offset
    response = await client.get("/students?limit=2&offset=2")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_list_students_validation_error_invalid_min_avg_grade(client: AsyncClient):
    """Test GET /students - validation error (invalid min_avg_grade)."""
    # min_avg_grade > 100
    response = await client.get("/students?min_avg_grade=101")
    
    assert response.status_code == 422
    
    # min_avg_grade < 0
    response = await client.get("/students?min_avg_grade=-1")
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_students_validation_error_invalid_limit(client: AsyncClient):
    """Test GET /students - validation error (invalid limit)."""
    # limit < 1
    response = await client.get("/students?limit=0")
    
    assert response.status_code == 422
    
    # limit > 1000
    response = await client.get("/students?limit=1001")
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_students_validation_error_invalid_offset(client: AsyncClient):
    """Test GET /students - validation error (invalid offset)."""
    # offset < 0
    response = await client.get("/students?offset=-1")
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_students_validation_error_invalid_sort_by(client: AsyncClient):
    """Test GET /students - validation error (invalid sort_by)."""
    response = await client.get("/students?sort_by=invalid_field")
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_students_validation_error_invalid_order(client: AsyncClient):
    """Test GET /students - validation error (invalid order)."""
    response = await client.get("/students?order=invalid")
    
    assert response.status_code == 422

