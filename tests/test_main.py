import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy.future import select
from sqlalchemy import text

from backend.app.models import LogMetric
from backend.app.schemas import LogCreate


class TestRootEndpoint:
    """Test cases for the root endpoint."""
    
    @pytest.mark.api
    def test_root_endpoint(self, client):
        """Test root endpoint returns correct message."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "API de Logs funcionando!"}


class TestCreateLogEndpoint:
    """Test cases for the create log endpoint."""
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_create_log_success(self, async_client, mock_celery, mock_async_session):
        """Test successful log creation."""
        mock_celery_app, mock_task = mock_celery
        mock_session = mock_async_session.return_value.__aenter__.return_value
        
        # Mock database query result
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        log_data = {
            "service": "test-service",
            "level": "ERROR",
            "message": "Test error",
            "timestamp": "2024-01-15T12:00:00",
            "metadata": {"user_id": 123}
        }
        
        response = await async_client.post("/logs/", json=log_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Log recebido e processando."
        assert data["task_id"] == "test-task-id-123"
        assert data["current_count"] == 0
        assert data["alert"] is None
        
        # Verify Celery task was called
        mock_task.delay.assert_called_once()
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_create_log_with_existing_metric(self, async_client, mock_celery, mock_async_session):
        """Test log creation when metric already exists."""
        mock_celery_app, mock_task = mock_celery
        mock_session = mock_async_session.return_value.__aenter__.return_value
        
        # Mock existing metric
        mock_metric = Mock()
        mock_metric.count = 3
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_metric
        mock_session.execute.return_value = mock_result
        
        log_data = {
            "service": "test-service",
            "level": "ERROR",
            "message": "Test error",
            "timestamp": "2024-01-15T12:00:00",
            "metadata": {"user_id": 123}
        }
        
        response = await async_client.post("/logs/", json=log_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["current_count"] == 3
        assert data["alert"] is None
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_create_log_trigger_alert(self, async_client, mock_celery, mock_async_session):
        """Test log creation that triggers an alert."""
        mock_celery_app, mock_task = mock_celery
        mock_session = mock_async_session.return_value.__aenter__.return_value
        
        # Mock existing metric with count >= threshold (5)
        mock_metric = Mock()
        mock_metric.count = 5
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_metric
        mock_session.execute.return_value = mock_result
        
        log_data = {
            "service": "test-service",
            "level": "ERROR",
            "message": "Test error",
            "timestamp": "2024-01-15T12:00:00",
            "metadata": {"user_id": 123}
        }
        
        response = await async_client.post("/logs/", json=log_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["current_count"] == 5
        assert "ALERTA:" in data["alert"]
        assert "5 ocorrências" in data["alert"]
        assert "ERROR" in data["alert"]
        assert "test-service" in data["alert"]
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_create_log_invalid_data(self, async_client):
        """Test log creation with invalid data."""
        invalid_data = {
            "service": "",  # Empty service
            "level": "INVALID_LEVEL",  # Invalid level
            "message": "",  # Empty message
            "timestamp": "invalid-timestamp",  # Invalid timestamp
        }
        
        response = await async_client.post("/logs/", json=invalid_data)
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_create_log_missing_required_fields(self, async_client):
        """Test log creation with missing required fields."""
        incomplete_data = {
            "service": "test-service",
            "level": "ERROR"
            # Missing message and timestamp
        }
        
        response = await async_client.post("/logs/", json=incomplete_data)
        assert response.status_code == 422
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_create_log_database_error(self, async_client, mock_celery, mock_async_session):
        """Test log creation when database error occurs."""
        mock_celery_app, mock_task = mock_celery
        mock_session = mock_async_session.return_value.__aenter__.return_value
        
        # Mock database error
        mock_session.execute.side_effect = Exception("Database connection failed")
        
        log_data = {
            "service": "test-service",
            "level": "ERROR",
            "message": "Test error",
            "timestamp": "2024-01-15T12:00:00",
            "metadata": {"user_id": 123}
        }
        
        response = await async_client.post("/logs/", json=log_data)
        assert response.status_code == 500
        assert "Database connection failed" in response.json()["detail"]


class TestGetTaskStatusEndpoint:
    """Test cases for the get task status endpoint."""
    
    @pytest.mark.api
    def test_get_task_status_success(self, client, mock_async_result):
        """Test successful task status retrieval."""
        response = client.get("/tasks/test-task-id-123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "test-task-id-123"
        assert data["status"] == "SUCCESS"
        assert data["result"] == {"processed": True}
    
    @pytest.mark.api
    def test_get_task_status_different_statuses(self, client):
        """Test task status with different status values."""
        with patch('backend.app.main.AsyncResult') as mock_result:
            # Test PENDING status
            mock_result.return_value.status = "PENDING"
            mock_result.return_value.result = None
            
            response = client.get("/tasks/test-task-id-456")
            assert response.status_code == 200
            assert response.json()["status"] == "PENDING"
            
            # Test FAILURE status
            mock_result.return_value.status = "FAILURE"
            mock_result.return_value.result = "Task failed"
            
            response = client.get("/tasks/test-task-id-789")
            assert response.status_code == 200
            assert response.json()["status"] == "FAILURE"
            assert response.json()["result"] == "Task failed"


class TestGetLogsByServiceEndpoint:
    """Test cases for the get logs by service endpoint."""
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_logs_by_service_success(self, async_client, mock_async_session):
        """Test successful retrieval of logs by service."""
        mock_session = mock_async_session.return_value.__aenter__.return_value
        
        # Mock database results
        mock_logs = [
            Mock(service="test-service", level="ERROR", count=5, timestamp=datetime.now()),
            Mock(service="test-service", level="WARN", count=3, timestamp=datetime.now()),
        ]
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_logs
        mock_session.execute.return_value = mock_result
        
        response = await async_client.get("/logs/service/test-service")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["service"] == "test-service"
        assert data[0]["level"] == "ERROR"
        assert data[0]["count"] == 5
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_logs_by_service_with_limit(self, async_client, mock_async_session):
        """Test logs retrieval with custom limit."""
        mock_session = mock_async_session.return_value.__aenter__.return_value
        
        # Mock database results
        mock_logs = [Mock(service="test-service", level="ERROR", count=1, timestamp=datetime.now())]
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_logs
        mock_session.execute.return_value = mock_result
        
        response = await async_client.get("/logs/service/test-service?limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_logs_by_service_no_logs(self, async_client, mock_async_session):
        """Test logs retrieval when no logs exist for service."""
        mock_session = mock_async_session.return_value.__aenter__.return_value
        
        # Mock empty results
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result
        
        response = await async_client.get("/logs/service/nonexistent-service")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_logs_by_service_database_error(self, async_client, mock_async_session):
        """Test logs retrieval when database error occurs."""
        mock_session = mock_async_session.return_value.__aenter__.return_value
        
        # Mock database error
        mock_session.execute.side_effect = Exception("Database error")
        
        response = await async_client.get("/logs/service/test-service")
        assert response.status_code == 500


class TestGetLogsByLevelEndpoint:
    """Test cases for the get logs by level endpoint."""
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_logs_by_level_success(self, async_client, mock_async_session):
        """Test successful retrieval of logs by level."""
        mock_session = mock_async_session.return_value.__aenter__.return_value
        
        # Mock database results
        mock_logs = [
            Mock(service="service-a", level="ERROR", count=5, timestamp=datetime.now()),
            Mock(service="service-b", level="ERROR", count=3, timestamp=datetime.now()),
        ]
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_logs
        mock_session.execute.return_value = mock_result
        
        response = await async_client.get("/logs/level/ERROR")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(log["level"] == "ERROR" for log in data)
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_logs_by_level_with_limit(self, async_client, mock_async_session):
        """Test logs retrieval by level with custom limit."""
        mock_session = mock_async_session.return_value.__aenter__.return_value
        
        # Mock database results
        mock_logs = [Mock(service="service-a", level="WARN", count=2, timestamp=datetime.now())]
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_logs
        mock_session.execute.return_value = mock_result
        
        response = await async_client.get("/logs/level/WARN?limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1


class TestGetMetricsByServiceEndpoint:
    """Test cases for the get metrics by service endpoint."""
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_metrics_by_service_success(self, async_client, mock_async_session):
        """Test successful retrieval of metrics by service."""
        mock_session = mock_async_session.return_value.__aenter__.return_value
        
        # Mock database results
        mock_logs = [
            Mock(service="test-service", level="ERROR", count=5, timestamp=datetime.now()),
            Mock(service="test-service", level="WARN", count=3, timestamp=datetime.now()),
            Mock(service="test-service", level="INFO", count=10, timestamp=datetime.now()),
        ]
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_logs
        mock_session.execute.return_value = mock_result
        
        response = await async_client.get("/metrics/service/test-service")
        
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "test-service"
        assert data["metrics"]["ERROR"] == 5
        assert data["metrics"]["WARN"] == 3
        assert data["metrics"]["INFO"] == 10
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_metrics_by_service_with_date_range(self, async_client, mock_async_session):
        """Test metrics retrieval with date range filters."""
        mock_session = mock_async_session.return_value.__aenter__.return_value
        
        # Mock database results
        mock_logs = [Mock(service="test-service", level="ERROR", count=5, timestamp=datetime.now())]
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_logs
        mock_session.execute.return_value = mock_result
        
        start_date = "2024-01-01T00:00:00"
        end_date = "2024-01-31T23:59:59"
        
        response = await async_client.get(f"/metrics/service/test-service?start={start_date}&end={end_date}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "test-service"
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_metrics_by_service_no_metrics(self, async_client, mock_async_session):
        """Test metrics retrieval when no metrics exist for service."""
        mock_session = mock_async_session.return_value.__aenter__.return_value
        
        # Mock empty results
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result
        
        response = await async_client.get("/metrics/service/nonexistent-service")
        
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "nonexistent-service"
        assert data["metrics"] == {}


class TestGetMetricsByLevelEndpoint:
    """Test cases for the get metrics by level endpoint."""
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_metrics_by_level_success(self, async_client, mock_async_session):
        """Test successful retrieval of metrics by level."""
        mock_session = mock_async_session.return_value.__aenter__.return_value
        
        # Mock database results
        mock_logs = [
            Mock(service="service-a", level="ERROR", count=5, timestamp=datetime.now()),
            Mock(service="service-b", level="ERROR", count=3, timestamp=datetime.now()),
            Mock(service="service-c", level="ERROR", count=7, timestamp=datetime.now()),
        ]
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_logs
        mock_session.execute.return_value = mock_result
        
        response = await async_client.get("/metrics/level/ERROR")
        
        assert response.status_code == 200
        data = response.json()
        assert data["level"] == "ERROR"
        assert data["metrics"]["service-a"] == 5
        assert data["metrics"]["service-b"] == 3
        assert data["metrics"]["service-c"] == 7
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_metrics_by_level_with_date_range(self, async_client, mock_async_session):
        """Test metrics retrieval by level with date range filters."""
        mock_session = mock_async_session.return_value.__aenter__.return_value
        
        # Mock database results
        mock_logs = [Mock(service="service-a", level="WARN", count=2, timestamp=datetime.now())]
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_logs
        mock_session.execute.return_value = mock_result
        
        start_date = "2024-01-01T00:00:00"
        end_date = "2024-01-31T23:59:59"
        
        response = await async_client.get(f"/metrics/level/WARN?start={start_date}&end={end_date}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["level"] == "WARN"


class TestGetAlertsEndpoint:
    """Test cases for the get alerts endpoint."""
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_alerts_success(self, async_client, mock_async_session):
        """Test successful retrieval of alerts."""
        mock_session = mock_async_session.return_value.__aenter__.return_value
        
        # Mock database results with count >= threshold (5)
        mock_logs = [
            Mock(service="service-a", level="ERROR", count=7, timestamp=datetime.now()),
            Mock(service="service-b", level="ERROR", count=5, timestamp=datetime.now()),
        ]
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_logs
        mock_session.execute.return_value = mock_result
        
        response = await async_client.get("/alerts/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(alert["count"] >= 5 for alert in data)
        assert all("ALERT:" in alert["alert"] for alert in data)
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_alerts_with_filters(self, async_client, mock_async_session):
        """Test alerts retrieval with various filters."""
        mock_session = mock_async_session.return_value.__aenter__.return_value
        
        # Mock database results
        mock_logs = [Mock(service="service-a", level="ERROR", count=6, timestamp=datetime.now())]
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_logs
        mock_session.execute.return_value = mock_result
        
        # Test with service filter
        response = await async_client.get("/alerts/?service=service-a")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["service"] == "service-a"
        
        # Test with level filter
        response = await async_client.get("/alerts/?level=ERROR")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["level"] == "ERROR"
        
        # Test with limit
        response = await async_client.get("/alerts/?limit=5")
        assert response.status_code == 200
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_alerts_no_alerts(self, async_client, mock_async_session):
        """Test alerts retrieval when no alerts exist."""
        mock_session = mock_async_session.return_value.__aenter__.return_value
        
        # Mock empty results
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result
        
        response = await async_client.get("/alerts/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_get_alerts_with_date_range(self, async_client, mock_async_session):
        """Test alerts retrieval with date range filters."""
        mock_session = mock_async_session.return_value.__aenter__.return_value
        
        # Mock database results
        mock_logs = [Mock(service="service-a", level="ERROR", count=6, timestamp=datetime.now())]
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_logs
        mock_session.execute.return_value = mock_result
        
        start_date = "2024-01-01T00:00:00"
        end_date = "2024-01-31T23:59:59"
        
        response = await async_client.get(f"/alerts/?start={start_date}&end={end_date}")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
