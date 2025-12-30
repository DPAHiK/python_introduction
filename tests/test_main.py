import pytest
import json
import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock
from script.main import main
from script.db import AsyncDB

class TestMain:
    """Test cases for the main module."""
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock AsyncDB instance."""
        with patch('script.main.AsyncDB') as mock_db_class:
            mock_db = AsyncMock()
            mock_db_class.return_value = mock_db
            mock_db.__aenter__.return_value = mock_db
            mock_db.__aexit__.return_value = None
            yield mock_db

    @pytest.fixture
    def test_data(self, tmp_path):
        """Create test data files."""
        # Sample test data
        students = [
            {
                "id": 1,
                "name": "John Doe",
                "birthday": "2000-01-01T00:00:00.000000",
                "sex": "M",
                "room": 1
            },
            {
                "id": 2,
                "name": "Jane Smith",
                "birthday": "2001-02-15T00:00:00.000000",
                "sex": "F",
                "room": 1
            }
        ]
        
        rooms = [
            {"id": 1, "name": "Room 1"},
            {"id": 2, "name": "Room 2"}
        ]
        
        # Create temporary files
        students_file = tmp_path / "students.json"
        rooms_file = tmp_path / "rooms.json"
        
        with open(students_file, 'w') as f:
            json.dump(students, f)
        
        with open(rooms_file, 'w') as f:
            json.dump(rooms, f)
        
        return {
            'students_path': str(students_file),
            'rooms_path': str(rooms_file),
            'students': students,
            'rooms': rooms
        }

    @pytest.mark.asyncio
    async def test_main_success(self, test_data, mock_db):
        """Test main function with valid inputs."""
        # Call the main function with test data
        await main(
            students_path=test_data['students_path'],
            rooms_path=test_data['rooms_path'],
            format="json"
        )
        
        # Verify database operations
        assert mock_db.executemany.call_count >= 2  # At least 2 calls for rooms and students
        
        # Verify the first call was for rooms
        args, kwargs = mock_db.executemany.call_args_list[0]
        assert "INSERT INTO rooms" in args[0]
        
        # Verify the second call was for students
        args, kwargs = mock_db.executemany.call_args_list[1]
        assert "INSERT INTO students" in args[0]
        
        # Verify execute_and_save was called (for queries)
        assert mock_db.execute_and_save.called

    @pytest.mark.asyncio
    async def test_main_invalid_format(self, test_data, mock_db):
        """Test main function with invalid format."""
        # Call with invalid format
        await main(
            students_path=test_data['students_path'],
            rooms_path=test_data['rooms_path'],
            format="invalid"
        )
        
        # Verify no database operations were performed
        assert not mock_db.executemany.called
        assert not mock_db.execute_and_save.called

    @pytest.mark.asyncio
    async def test_main_missing_files(self, test_data, mock_db):
        """Test main function with missing files."""
        # Test with non-existent files
        with pytest.raises(FileNotFoundError):
            await main(
                students_path="nonexistent_students.json",
                rooms_path="nonexistent_rooms.json",
                format="json"
            )
        
        # Verify no database operations were performed
        assert not mock_db.executemany.called
        assert not mock_db.execute_and_save.called

    @pytest.mark.asyncio
    async def test_main_invalid_json(self, test_data, mock_db, tmp_path):
        """Test main function with invalid JSON files."""
        # Create invalid JSON file
        invalid_json = tmp_path / "invalid.json"
        with open(invalid_json, 'w') as f:
            f.write("This is not valid JSON")
        
        # Test with invalid students JSON
        with pytest.raises(json.JSONDecodeError):
            await main(
                students_path=str(invalid_json),
                rooms_path=test_data['rooms_path'],
                format="json"
            )
        
        # Test with invalid rooms JSON
        with pytest.raises(json.JSONDecodeError):
            await main(
                students_path=test_data['students_path'],
                rooms_path=str(invalid_json),
                format="json"
            )
        
        # Verify no database operations were performed
        assert not mock_db.executemany.called
        assert not mock_db.execute_and_save.called

    @pytest.mark.asyncio
    async def test_main_date_parsing(self, test_data, mock_db):
        """Test date parsing in the main function."""
        # Call the main function with test data
        await main(
            students_path=test_data['students_path'],
            rooms_path=test_data['rooms_path'],
            format="json"
        )
        
        # Find the call that inserts students
        for call in mock_db.executemany.call_args_list:
            if "INSERT INTO students" in call[0][0]:
                student_values = call[0][1]
                # Check that the birthday was parsed correctly
                for student in student_values:
                    # The birthday should be the 4th element (0-based index 3)
                    assert isinstance(student[3], datetime.datetime)
                break
        else:
            assert False, "No student insert call found"
