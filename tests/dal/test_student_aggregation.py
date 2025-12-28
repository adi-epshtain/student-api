"""Tests for student aggregation queries."""
import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.dal.student import list_students_with_avg
from app.models.grade import Grade
from app.models.student import Student


@pytest.fixture
async def test_students(db_session: AsyncSession) -> list[Student]:
    """Create test students."""
    students = [
        Student(id=uuid.uuid4(), name="Alice"),
        Student(id=uuid.uuid4(), name="Bob"),
        Student(id=uuid.uuid4(), name="Charlie"),
        Student(id=uuid.uuid4(), name="Diana"),
    ]
    for student in students:
        db_session.add(student)
    await db_session.commit()
    for student in students:
        await db_session.refresh(student)
    return students


@pytest.fixture
async def test_grades(db_session: AsyncSession, test_students: list[Student]) -> list[Grade]:
    """Create test grades for students."""
    # Alice: grades [80, 90, 100] -> avg = 90.0
    # Bob: grades [70, 80] -> avg = 75.0
    # Charlie: no grades -> avg = None
    # Diana: grade [95] -> avg = 95.0
    
    grades = [
        Grade(id=uuid.uuid4(), student_id=test_students[0].id, score=80),  # Alice
        Grade(id=uuid.uuid4(), student_id=test_students[0].id, score=90),  # Alice
        Grade(id=uuid.uuid4(), student_id=test_students[0].id, score=100),  # Alice
        Grade(id=uuid.uuid4(), student_id=test_students[1].id, score=70),  # Bob
        Grade(id=uuid.uuid4(), student_id=test_students[1].id, score=80),  # Bob
        Grade(id=uuid.uuid4(), student_id=test_students[3].id, score=95),  # Diana
    ]
    for grade in grades:
        db_session.add(grade)
    await db_session.commit()
    for grade in grades:
        await db_session.refresh(grade)
    return grades


@pytest.mark.asyncio
async def test_avg_grade_calculation(
    db_session: AsyncSession,
    test_students: list[Student],
    test_grades: list[Grade],
):
    """Test that average grade is calculated correctly using SQL aggregation."""
    results = await list_students_with_avg(db_session)
    
    # Find students by name
    alice = next((s, avg) for s, avg in results if s.name == "Alice")
    bob = next((s, avg) for s, avg in results if s.name == "Bob")
    diana = next((s, avg) for s, avg in results if s.name == "Diana")
    
    # Alice: (80 + 90 + 100) / 3 = 90.0
    assert alice[1] == 90.0, "Alice's average should be 90.0"
    
    # Bob: (70 + 80) / 2 = 75.0
    assert bob[1] == 75.0, "Bob's average should be 75.0"
    
    # Diana: 95 / 1 = 95.0
    assert diana[1] == 95.0, "Diana's average should be 95.0"


@pytest.mark.asyncio
async def test_students_without_grades(
    db_session: AsyncSession,
    test_students: list[Student],
    test_grades: list[Grade],
):
    """Test that students without grades return None for avg_grade."""
    results = await list_students_with_avg(db_session)
    
    # Find Charlie (no grades)
    charlie = next((s, avg) for s, avg in results if s.name == "Charlie")
    
    # Charlie has no grades, so avg_grade should be None
    assert charlie[1] is None, "Charlie should have None avg_grade (no grades)"
    
    # Verify all students are included (LEFT JOIN)
    assert len(results) == 4, "All 4 students should be returned"


@pytest.mark.asyncio
async def test_min_avg_grade_filtering_with_having(
    db_session: AsyncSession,
    test_students: list[Student],
    test_grades: list[Grade],
):
    """Test min_avg_grade filtering using HAVING clause."""
    # Filter for students with avg >= 85
    results = await list_students_with_avg(db_session, min_avg_grade=85.0)
    
    # Should only return Alice (90.0) and Diana (95.0)
    # Bob (75.0) and Charlie (None) should be excluded
    assert len(results) == 2, "Should return 2 students with avg >= 85"
    
    names = {s.name for s, _ in results}
    assert "Alice" in names, "Alice should be included (avg=90.0)"
    assert "Diana" in names, "Diana should be included (avg=95.0)"
    assert "Bob" not in names, "Bob should be excluded (avg=75.0)"
    assert "Charlie" not in names, "Charlie should be excluded (no grades)"
    
    # Verify averages are correct
    alice_avg = next(avg for s, avg in results if s.name == "Alice")
    diana_avg = next(avg for s, avg in results if s.name == "Diana")
    assert alice_avg == 90.0
    assert diana_avg == 95.0


@pytest.mark.asyncio
async def test_min_avg_grade_excludes_students_without_grades(
    db_session: AsyncSession,
    test_students: list[Student],
    test_grades: list[Grade],
):
    """Test that min_avg_grade filter excludes students without grades (HAVING clause)."""
    # Filter for students with avg >= 0 (should still exclude students without grades)
    results = await list_students_with_avg(db_session, min_avg_grade=0.0)
    
    # Should return Alice, Bob, Diana (all have grades)
    # Charlie (no grades) should be excluded by HAVING clause
    assert len(results) == 3, "Should return 3 students with grades"
    
    names = {s.name for s, _ in results}
    assert "Alice" in names
    assert "Bob" in names
    assert "Diana" in names
    assert "Charlie" not in names, "Charlie should be excluded (no grades, NULL avg)"


@pytest.mark.asyncio
async def test_min_avg_grade_boundary_value(
    db_session: AsyncSession,
    test_students: list[Student],
    test_grades: list[Grade],
):
    """Test min_avg_grade with boundary values."""
    # Filter for avg >= 90.0 (exact match)
    results = await list_students_with_avg(db_session, min_avg_grade=90.0)
    
    names = {s.name for s, _ in results}
    assert "Alice" in names, "Alice (90.0) should be included (>= 90.0)"
    assert "Diana" in names, "Diana (95.0) should be included"
    assert "Bob" not in names, "Bob (75.0) should be excluded"
    
    # Filter for avg >= 90.1 (just above Alice's average)
    results = await list_students_with_avg(db_session, min_avg_grade=90.1)
    
    names = {s.name for s, _ in results}
    assert "Alice" not in names, "Alice (90.0) should be excluded (< 90.1)"
    assert "Diana" in names, "Diana (95.0) should be included"


@pytest.mark.asyncio
async def test_aggregation_with_single_grade(
    db_session: AsyncSession,
    test_students: list[Student],
    test_grades: list[Grade],
):
    """Test that single grade returns correct average."""
    results = await list_students_with_avg(db_session)
    
    # Diana has only one grade (95)
    diana = next((s, avg) for s, avg in results if s.name == "Diana")
    assert diana[1] == 95.0, "Single grade should return that grade as average"

