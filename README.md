# Students Grades API

A REST API for managing students and their grades. 

## Tech Stack

- **FastAPI** - Modern async web framework
- **SQLAlchemy 2.0** - Async ORM with declarative models
- **SQLite** - Database (configurable to PostgreSQL)
- **Pydantic** - Data validation and serialization
- **pytest** - Testing framework with async support

## Setup

```bash
# Create and activate virtual environment
python -m venv venv

# Activiate venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`. Interactive API documentation at `http://localhost:8000/docs`.

## Running Tests

```bash
# Run all tests
pytest
```

## API Overview

### Students

**POST `/students`**
- Create a new student
- Request body: `{"name": "string"}` (1-100 characters)
- Returns: `201 Created` with student data

**GET `/students`**
- List students with average grades
- Query parameters:
  - `min_avg_grade` (float, 0-100): Filter by minimum average grade
  - `sort_by` (string): `name`, `avg_grade`, or `created_at` (default: `name`)
  - `order` (string): `asc` or `desc` (default: `asc`)
  - `limit` (int, 1-1000): Results per page (default: 100)
  - `offset` (int, ≥0): Pagination offset (default: 0)
- Returns: `200 OK` with list of students including `avg_grade`

### Grades

**POST `/students/{student_id}/grades`**
- Add a grade for a student
- Path parameter: `student_id` (UUID)
- Request body: `{"score": int}` (0-100)
- Returns: `201 Created` with grade data
- Errors: `404 Not Found` if student doesn't exist, `422` for validation errors

