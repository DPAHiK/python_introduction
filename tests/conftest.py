import pytest
import asyncio
import asyncpg
from pathlib import Path
from script.config import settings

# Test database configuration
TEST_DB = "test_db"
TEST_USER = settings.db_user
TEST_PASSWORD = settings.db_pass
TEST_HOST = settings.db_host

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_db():
    """Create a test database and yield connection parameters."""
    # Connect to the default postgres database to create our test database
    conn = await asyncpg.connect(
        database="postgres",
        user=TEST_USER,
        password=TEST_PASSWORD,
        host=TEST_HOST
    )
    
    # Create test database
    await conn.execute(f"DROP DATABASE IF EXISTS {TEST_DB}")
    await conn.execute(f"CREATE DATABASE {TEST_DB}")
    await conn.close()
    
    # Connect to the test database to set up tables
    conn = await asyncpg.connect(
        database=TEST_DB,
        user=TEST_USER,
        password=TEST_PASSWORD,
        host=TEST_HOST
    )
    
    # Create tables (simplified schema for testing)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY,
            name TEXT
        )
    """)
    
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY,
            name TEXT,
            sex TEXT,
            birthday TIMESTAMP,
            room INTEGER
        )
    """)
    
    yield TEST_DB
    
    # Cleanup
    await conn.close()
    
    # Drop test database
    admin_conn = await asyncpg.connect(
        database="postgres",
        user=TEST_USER,
        password=TEST_PASSWORD,
        host=TEST_HOST
    )
    await admin_conn.execute(f"""
        SELECT pg_terminate_backend(pid) 
        FROM pg_stat_activity 
        WHERE datname = '{TEST_DB}'
    """)
    await admin_conn.execute(f"DROP DATABASE {TEST_DB}")
    await admin_conn.close()

@pytest.fixture
def test_data():
    """Provide test data for database operations."""
    return {
        "rooms": [
            (1, "Room 1"),
            (2, "Room 2"),
            (3, "Room 3")
        ],
        "students": [
            (1, "John Doe", "M", "2000-01-01T00:00:00.000000", 1),
            (2, "Jane Smith", "F", "2001-02-15T00:00:00.000000", 1),
            (3, "Bob Johnson", "M", "1999-12-31T00:00:00.000000", 2)
        ]
    }
