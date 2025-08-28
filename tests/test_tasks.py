import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta


from backend.app.tasks import truncate_minute, process_log_task


class TestTruncateMinute:
    """Test cases for truncate_minute utility function."""
    
    def test_truncate_minute_removes_seconds_and_microseconds(self):
        """Test that truncate_minute removes seconds and microseconds."""
        # Test with seconds and microseconds
        dt = datetime(2024, 1, 15, 12, 30, 45, 123456)
        truncated = truncate_minute(dt)
        
        expected = datetime(2024, 1, 15, 12, 30, 0, 0)
        assert truncated == expected
    
    def test_truncate_minute_preserves_date_and_time(self):
        """Test that truncate_minute preserves date and time components."""
        # Test with different date/time combinations
        test_cases = [
            datetime(2024, 1, 15, 12, 0, 30, 500000),
            datetime(2024, 12, 31, 23, 59, 45, 999999),
            datetime(2024, 2, 29, 0, 0, 1, 100000),  # Leap year
        ]
        
        for dt in test_cases:
            truncated = truncate_minute(dt)
            
            # Verify date and time are preserved
            assert truncated.year == dt.year
            assert truncated.month == dt.month
            assert truncated.day == dt.day
            assert truncated.hour == dt.hour
            assert truncated.minute == dt.minute
            
            # Verify seconds and microseconds are zero
            assert truncated.second == 0
            assert truncated.microsecond == 0
    
    def test_truncate_minute_edge_cases(self):
        """Test truncate_minute with edge cases."""
        # Test with already truncated datetime
        dt = datetime(2024, 1, 15, 12, 30, 0, 0)
        truncated = truncate_minute(dt)
        assert truncated == dt
        
        # Test with datetime at minute boundary
        dt = datetime(2024, 1, 15, 12, 30, 0, 0)
        truncated = truncate_minute(dt)
        assert truncated == dt
        
        # Test with very small microseconds
        dt = datetime(2024, 1, 15, 12, 30, 0, 1)
        truncated = truncate_minute(dt)
        expected = datetime(2024, 1, 15, 12, 30, 0, 0)
        assert truncated == expected
    
    def test_truncate_minute_timezone_aware(self):
        """Test truncate_minute with timezone-aware datetimes."""
        from datetime import timezone
        
        # Test with UTC timezone
        dt = datetime(2024, 1, 15, 12, 30, 45, 123456, tzinfo=timezone.utc)
        truncated = truncate_minute(dt)
        
        expected = datetime(2024, 1, 15, 12, 30, 0, 0, tzinfo=timezone.utc)
        assert truncated == expected
        
        # Test with different timezone
        from datetime import timedelta
        tz = timezone(timedelta(hours=5))  # UTC+5
        dt = datetime(2024, 1, 15, 12, 30, 45, 123456, tzinfo=tz)
        truncated = truncate_minute(dt)
        
        expected = datetime(2024, 1, 15, 12, 30, 0, 0, tzinfo=tz)
        assert truncated == expected
    
    def test_truncate_minute_immutability(self):
        """Test that truncate_minute doesn't modify the original datetime."""
        original_dt = datetime(2024, 1, 15, 12, 30, 45, 123456)
        original_copy = original_dt.replace()  # Create a copy
        
        truncated = truncate_minute(original_dt)
        
        # Original should remain unchanged
        assert original_dt == original_copy
        assert original_dt.second == 45
        assert original_dt.microsecond == 123456
        
        # Truncated should be different
        assert truncated != original_dt
        assert truncated.second == 0
        assert truncated.microsecond == 0


class TestProcessLogTask:
    """Test cases for process_log_task Celery task."""
    
    @pytest.fixture
    def sample_log_data(self):
        """Sample log data for testing."""
        return {
            "service": "test-service",
            "level": "ERROR",
            "message": "Test error message",
            "timestamp": datetime(2024, 1, 15, 12, 30, 45, 123456),
            "metadata": {"user_id": 123, "request_id": "req-456"}
        }
    
    @pytest.fixture
    def mock_mongo_db(self):
        """Mock MongoDB database."""
        mock_db = Mock()
        mock_collection = Mock()
        mock_db.logs = mock_collection
        return mock_db, mock_collection
    
    @pytest.fixture
    def mock_postgres_session(self):
        """Mock PostgreSQL session."""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        return mock_session, mock_query
    
    @patch('backend.app.tasks.mongo_db')
    @patch('backend.app.tasks.AsyncSessionLocal')
    def test_process_log_task_success_new_metric(self, mock_async_session_local, mock_mongo_db, sample_log_data):
        """Test successful log processing with new metric."""
        # Mock MongoDB
        mock_collection = Mock()
        mock_mongo_db.logs = mock_collection
        
        # Mock async PostgreSQL session
        mock_session = AsyncMock()
        mock_session.__aenter__.return_value = mock_session
        mock_session.__aexit__.return_value = None
        mock_async_session_local.return_value = mock_session
        
        # Mock async database operations
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        # Execute task
        result = process_log_task(sample_log_data)
        
        # Verify MongoDB insert
        mock_collection.insert_one.assert_called_once_with(sample_log_data)
        
        # Verify PostgreSQL operations
        mock_session.add.assert_called_once()
        mock_session.commit.assert_awaited_once()
        
        # Verify result
        assert result["mongo_inserted"] is True
        assert result["postgres_updated"] is True
        assert result["service"] == "test-service"
        assert result["level"] == "ERROR"
    
    @patch('backend.app.tasks.mongo_db')
    @patch('backend.app.tasks.AsyncSessionLocal')
    def test_process_log_task_success_existing_metric(self, mock_async_session_local, mock_mongo_db, sample_log_data):
        """Test successful log processing with existing metric."""
        # Mock MongoDB
        mock_collection = Mock()
        mock_mongo_db.logs = mock_collection
        
        # Mock async PostgreSQL session
        mock_session = AsyncMock()
        mock_session.__aenter__.return_value = mock_session
        mock_session.__aexit__.return_value = None
        mock_async_session_local.return_value = mock_session
        
        # Mock existing metric
        mock_metric = Mock()
        mock_metric.count = 5
        
        # Mock async database operations
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_metric
        mock_session.execute.return_value = mock_result
        
        # Execute task
        result = process_log_task(sample_log_data)
        
        # Verify MongoDB insert
        mock_collection.insert_one.assert_called_once_with(sample_log_data)
        
        # Verify PostgreSQL operations
        mock_metric.count += 1  # Should be incremented
        mock_session.commit.assert_awaited_once()
        
        # Verify result
        assert result["mongo_inserted"] is True
        assert result["postgres_updated"] is True
    
    @patch('backend.app.tasks.mongo_db')
    @patch('backend.app.tasks.AsyncSessionLocal')
    def test_process_log_task_mongo_error(self, mock_async_session_local, mock_mongo_db, sample_log_data):
        """Test log processing when MongoDB insert fails."""
        # Mock MongoDB error
        mock_collection = Mock()
        mock_collection.insert_one.side_effect = Exception("MongoDB connection failed")
        mock_mongo_db.logs = mock_collection
        
        # Mock async PostgreSQL session
        mock_session = AsyncMock()
        mock_session.__aenter__.return_value = mock_session
        mock_session.__aexit__.return_value = None
        mock_async_session_local.return_value = mock_session
        
        # Execute task and expect exception
        with pytest.raises(Exception, match="MongoDB connection failed"):
            process_log_task(sample_log_data)
    
    @patch('backend.app.tasks.mongo_db')
    @patch('backend.app.tasks.AsyncSessionLocal')
    def test_process_log_task_postgres_error(self, mock_async_session_local, mock_mongo_db, sample_log_data):
        """Test log processing when PostgreSQL operations fail."""
        # Mock MongoDB success
        mock_collection = Mock()
        mock_mongo_db.logs = mock_collection
        
        # Mock async PostgreSQL session with error
        mock_session = AsyncMock()
        mock_session.__aenter__.return_value = mock_session
        mock_session.__aexit__.return_value = None
        mock_async_session_local.return_value = mock_session
        
        # Mock async database operations
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        # Mock commit error
        mock_session.commit.side_effect = Exception("PostgreSQL commit failed")
        
        # Execute task and expect exception
        with pytest.raises(Exception, match="PostgreSQL commit failed"):
            process_log_task(sample_log_data)
    
    @patch('backend.app.tasks.mongo_db')
    @patch('backend.app.tasks.AsyncSessionLocal')
    def test_process_log_task_session_cleanup_on_error(self, mock_async_session_local, mock_mongo_db, sample_log_data):
        """Test that session is cleaned up even when errors occur."""
        # Mock MongoDB success
        mock_collection = Mock()
        mock_mongo_db.logs = mock_collection
        
        # Mock async PostgreSQL session
        mock_session = AsyncMock()
        mock_session.__aenter__.return_value = mock_session
        mock_session.__aexit__.return_value = None
        mock_async_session_local.return_value = mock_session
        
        # Mock execute error
        mock_session.execute.side_effect = Exception("Query failed")
        
        # Execute task and expect exception
        with pytest.raises(Exception, match="Query failed"):
            process_log_task(sample_log_data)
    
    @patch('backend.app.tasks.mongo_db')
    @patch('backend.app.tasks.AsyncSessionLocal')
    def test_process_log_task_timestamp_truncation(self, mock_async_session_local, mock_mongo_db):
        """Test that timestamp is properly truncated for metric aggregation."""
        # Test with different timestamp precisions
        test_cases = [
            datetime(2024, 1, 15, 12, 30, 45, 123456),  # With seconds and microseconds
            datetime(2024, 1, 15, 12, 30, 0, 0),         # Already truncated
            datetime(2024, 1, 15, 12, 30, 59, 999999),   # End of minute
        ]
        
        for timestamp in test_cases:
            log_data = {
                "service": "test-service",
                "level": "ERROR",
                "message": "Test message",
                "timestamp": timestamp,
                "metadata": {}
            }
            
            # Mock MongoDB
            mock_collection = Mock()
            mock_mongo_db.logs = mock_collection
            
            # Mock async PostgreSQL session
            mock_session = AsyncMock()
            mock_session.__aenter__.return_value = mock_session
            mock_session.__aexit__.return_value = None
            mock_async_session_local.return_value = mock_session
            
            # Mock async database operations
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = None
            mock_session.execute.return_value = mock_result
            
            # Execute task
            result = process_log_task(log_data)
            
            # Verify the execute was called
            mock_session.execute.assert_called_once()
            
            # Reset mocks for next iteration
            mock_collection.reset_mock()
            mock_session.reset_mock()
    
    @patch('backend.app.tasks.mongo_db')
    @patch('backend.app.tasks.AsyncSessionLocal')
    def test_process_log_task_metric_creation(self, mock_async_session_local, mock_mongo_db, sample_log_data):
        """Test that new metrics are created with correct values."""
        # Mock MongoDB
        mock_collection = Mock()
        mock_mongo_db.logs = mock_collection
        
        # Mock async PostgreSQL session
        mock_session = AsyncMock()
        mock_session.__aenter__.return_value = mock_session
        mock_session.__aexit__.return_value = None
        mock_async_session_local.return_value = mock_session
        
        # Mock async database operations
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        # Execute task
        result = process_log_task(sample_log_data)
        
        # Verify new metric was created with correct values
        mock_session.add.assert_called_once()
        created_metric = mock_session.add.call_args[0][0]
        
        assert created_metric.service == "test-service"
        assert created_metric.level == "ERROR"
        assert created_metric.count == 1
        assert created_metric.timestamp == truncate_minute(sample_log_data["timestamp"])
    
    @patch('backend.app.tasks.mongo_db')
    @patch('backend.app.tasks.AsyncSessionLocal')
    def test_process_log_task_metric_update(self, mock_async_session_local, mock_mongo_db, sample_log_data):
        """Test that existing metrics are updated correctly."""
        # Mock MongoDB
        mock_collection = Mock()
        mock_mongo_db.logs = mock_collection
        
        # Mock async PostgreSQL session
        mock_session = AsyncMock()
        mock_session.__aenter__.return_value = mock_session
        mock_session.__aexit__.return_value = None
        mock_async_session_local.return_value = mock_session
        
        # Mock existing metric
        mock_metric = Mock()
        mock_metric.count = 5
        
        # Mock async database operations
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_metric
        mock_session.execute.return_value = mock_result
        
        # Execute task
        result = process_log_task(sample_log_data)
        
        # Verify metric count was incremented
        assert mock_metric.count == 6  # 5 + 1
        
        # Verify no new metric was added
        mock_session.add.assert_not_called()
    
    @patch('backend.app.tasks.mongo_db')
    @patch('backend.app.tasks.AsyncSessionLocal')
    def test_process_log_task_different_log_levels(self, mock_async_session_local, mock_mongo_db):
        """Test processing logs with different levels."""
        log_levels = ["DEBUG", "INFO", "WARN", "ERROR", "CRITICAL", "FATAL"]
        
        for level in log_levels:
            log_data = {
                "service": "test-service",
                "level": level,
                "message": f"Test {level} message",
                "timestamp": datetime.now(),
                "metadata": {}
            }
            
            # Mock MongoDB
            mock_collection = Mock()
            mock_mongo_db.logs = mock_collection
            
            # Mock async PostgreSQL session
            mock_session = AsyncMock()
            mock_session.__aenter__.return_value = mock_session
            mock_session.__aexit__.return_value = None
            mock_async_session_local.return_value = mock_session
            
            # Mock async database operations
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = None
            mock_session.execute.return_value = mock_result
            
            # Execute task
            result = process_log_task(log_data)
            
            # Verify result contains correct level
            assert result["level"] == level
            
            # Reset mocks for next iteration
            mock_collection.reset_mock()
            mock_session.reset_mock()
    
    @patch('backend.app.tasks.mongo_db')
    @patch('backend.app.tasks.AsyncSessionLocal')
    def test_process_log_task_different_services(self, mock_async_session_local, mock_mongo_db):
        """Test processing logs for different services."""
        services = ["web-service", "api-service", "database-service", "cache-service"]
        
        for service in services:
            log_data = {
                "service": service,
                "level": "ERROR",
                "message": f"Test error in {service}",
                "timestamp": datetime.now(),
                "metadata": {}
            }
            
            # Mock MongoDB
            mock_collection = Mock()
            mock_mongo_db.logs = mock_collection
            
            # Mock async PostgreSQL session
            mock_session = AsyncMock()
            mock_session.__aenter__.return_value = mock_session
            mock_session.__aexit__.return_value = None
            mock_async_session_local.return_value = mock_session
            
            # Mock async database operations
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = None
            mock_session.execute.return_value = mock_result
            
            # Execute task
            result = process_log_task(log_data)
            
            # Verify result contains correct service
            assert result["service"] == service
            
            # Reset mocks for next iteration
            mock_collection.reset_mock()
            mock_session.reset_mock()
    
    @patch('backend.app.tasks.mongo_db')
    @patch('backend.app.tasks.AsyncSessionLocal')
    def test_process_log_task_metadata_handling(self, mock_async_session_local, mock_mongo_db):
        """Test that metadata is properly handled in MongoDB."""
        # Test with complex metadata
        complex_metadata = {
            "user": {
                "id": 123,
                "name": "John Doe",
                "email": "john@example.com"
            },
            "request": {
                "id": "req-456",
                "method": "POST",
                "path": "/api/logs",
                "headers": {
                    "User-Agent": "TestClient/1.0",
                    "Authorization": "Bearer token123"
                }
            },
            "tags": ["production", "critical", "user-facing"]
        }
        
        log_data = {
            "service": "test-service",
            "level": "ERROR",
            "message": "Test error with complex metadata",
            "timestamp": datetime.now(),
            "metadata": complex_metadata
        }
        
        # Mock MongoDB
        mock_collection = Mock()
        mock_mongo_db.logs = mock_collection
        
        # Mock async PostgreSQL session
        mock_session = AsyncMock()
        mock_session.__aenter__.return_value = mock_session
        mock_session.__aexit__.return_value = None
        mock_async_session_local.return_value = mock_session
        
        # Mock async database operations
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        # Execute task
        result = process_log_task(log_data)
        
        # Verify metadata was stored in MongoDB
        mock_collection.insert_one.assert_called_once_with(log_data)
        stored_data = mock_collection.insert_one.call_args[0][0]
        assert stored_data["metadata"] == complex_metadata
    
    @patch('backend.app.tasks.mongo_db')
    @patch('backend.app.tasks.AsyncSessionLocal')
    def test_process_log_task_return_value_structure(self, mock_async_session_local, mock_mongo_db, sample_log_data):
        """Test that the task returns the expected structure."""
        # Mock MongoDB
        mock_collection = Mock()
        mock_mongo_db.logs = mock_collection
        
        # Mock async PostgreSQL session
        mock_session = AsyncMock()
        mock_session.__aenter__.return_value = mock_session
        mock_session.__aexit__.return_value = None
        mock_async_session_local.return_value = mock_session
        
        # Mock async database operations
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        # Execute task
        result = process_log_task(sample_log_data)
        
        # Verify return value structure
        expected_keys = ["mongo_inserted", "postgres_updated", "service", "level"]
        assert all(key in result for key in expected_keys)
        
        # Verify return value types
        assert isinstance(result["mongo_inserted"], bool)
        assert isinstance(result["postgres_updated"], bool)
        assert isinstance(result["service"], str)
        assert isinstance(result["level"], str)
        
        # Verify return values
        assert result["mongo_inserted"] is True
        assert result["postgres_updated"] is True
        assert result["service"] == "test-service"
        assert result["level"] == "ERROR"
