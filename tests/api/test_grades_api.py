"""API tests for grade endpoints."""
import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import get_db
from app.dal.student import create_student
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
async def test_create_grade_success(client: AsyncClient, db_session):
    """Test POST /students/{id}/grades - happy path."""
    # Create student first
    student = await create_student(db_session, StudentCreate(name="Alice"))
    
    response = await client.post(
        f"/students/{student.id}/grades",
        json={"score": 85},
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["student_id"] == str(student.id)
    assert data["score"] == 85
    assert "id" in data
    assert "created_at" in data
    assert uuid.UUID(data["id"])  # Valid UUID


@pytest.mark.asyncio
async def test_create_grade_student_not_found(client: AsyncClient):
    """Test POST /students/{id}/grades - 404 when student not found."""
    fake_student_id = uuid.uuid4()
    
    response = await client.post(
        f"/students/{fake_student_id}/grades",
        json={"score": 85},
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


@pytest.mark.asyncio
async def test_create_grade_validation_error_score_too_low(client: AsyncClient, db_session):
    """Test POST /students/{id}/grades - validation error (score < 0)."""
    student = await create_student(db_session, StudentCreate(name="Alice"))
    
    response = await client.post(
        f"/students/{student.id}/grades",
        json={"score": -1},
    )
    
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_create_grade_validation_error_score_too_high(client: AsyncClient, db_session):
    """Test POST /students/{id}/grades - validation error (score > 100)."""
    student = await create_student(db_session, StudentCreate(name="Alice"))
    
    response = await client.post(
        f"/students/{student.id}/grades",
        json={"score": 101},
    )
    
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_create_grade_validation_error_missing_score(client: AsyncClient, db_session):
    """Test POST /students/{id}/grades - validation error (missing score)."""
    student = await create_student(db_session, StudentCreate(name="Alice"))
    
    response = await client.post(
        f"/students/{student.id}/grades",
        json={},
    )
    
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_create_grade_boundary_values(client: AsyncClient, db_session):
    """Test POST /students/{id}/grades - boundary values (0 and 100)."""
    student = await create_student(db_session, StudentCreate(name="Alice"))
    
    # Test score = 0
    response = await client.post(
        f"/students/{student.id}/grades",
        json={"score": 0},
    )
    assert response.status_code == 201
    assert response.json()["score"] == 0
    
    # Test score = 100
    response = await client.post(
        f"/students/{student.id}/grades",
        json={"score": 100},
    )
    assert response.status_code == 201
    assert response.json()["score"] == 100


@pytest.mark.asyncio
async def test_create_grade_multiple_grades_for_student(client: AsyncClient, db_session):
    """Test POST /students/{id}/grades - multiple grades for same student."""
    student = await create_student(db_session, StudentCreate(name="Alice"))
    
    # Create multiple grades
    response1 = await client.post(
        f"/students/{student.id}/grades",
        json={"score": 80},
    )
    assert response1.status_code == 201
    
    response2 = await client.post(
        f"/students/{student.id}/grades",
        json={"score": 90},
    )
    assert response2.status_code == 201
    
    # Verify both grades were created
    assert response1.json()["student_id"] == str(student.id)
    assert response2.json()["student_id"] == str(student.id)
    assert response1.json()["id"] != response2.json()["id"]  # Different IDs


@pytest.mark.asyncio
async def test_create_grade_invalid_uuid_format(client: AsyncClient):
    """Test POST /students/{id}/grades - invalid UUID format."""
    response = await client.post(
        "/students/invalid-uuid/grades",
        json={"score": 85},
    )
    
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data

