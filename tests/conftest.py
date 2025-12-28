"""Pytest configuration and shared fixtures."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base

# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def db_session(test_engine):
    """Create a database session for testing."""
    from app.models.grade import Grade
    from app.models.student import Student
    from sqlalchemy import delete
    
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session_maker() as session:
        # Clean up all data before each test (grades first due to FK constraint)
        await session.execute(delete(Grade))
        await session.execute(delete(Student))
        await session.commit()
        
        yield session
        
        # Clean up after test (grades first due to FK constraint)
        await session.execute(delete(Grade))
        await session.execute(delete(Student))
        await session.commit()


@pytest.fixture
async def db(db_session):
    """Override get_db dependency for testing."""
    async def _get_db():
        yield db_session
    
    return _get_db

