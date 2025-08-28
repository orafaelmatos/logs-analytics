import asyncio
from copy import deepcopy
from unittest.mock import AsyncMock, Mock, patch
import pytest


class TestRootEndpoint:
    """Test cases for the root endpoint."""

    def test_root_endpoint(self, client):
        """Test root endpoint returns correct message."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "API de Logs funcionando!"}


class TestCreateLogEndpoint:
    """Test cases for the create log endpoint."""
    
    @pytest.mark.asyncio
    async def test_parallel_requests_trigger_celery(self, async_client, multiple_logs_data):
        """Stress test: send many requests concurrently and verify Celery received correct payloads."""

        # --- Step 1: Patch DB session ---
        fake_metric = Mock()
        fake_metric.count = 0
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = fake_metric
        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result
        mock_cm = AsyncMock()
        mock_cm.__aenter__.return_value = mock_session
        mock_cm.__aexit__.return_value = None

        received_payloads = []

        def capture_payload(payload):
            received_payloads.append(deepcopy(payload))
            mock_task = type("MockTask", (), {"id": "test-task-id-123"})()
            return mock_task

        with patch("backend.app.main.AsyncSessionLocal", return_value=mock_cm), \
            patch("backend.app.main.process_log_task") as mock_task:
            mock_task.delay.side_effect = capture_payload

            log_payloads = [
                {**log, "timestamp": log["timestamp"].isoformat()}
                for log in multiple_logs_data
                for _ in range(5)
            ]

            tasks = [async_client.post("/logs/", json=log) for log in log_payloads]
            responses = await asyncio.gather(*tasks)

            for response in responses:
                assert response.status_code == 200
                data = response.json()
                assert data["message"] == "Log recebido e processando."
                assert data["task_id"] == "test-task-id-123"

            assert mock_task.delay.call_count == len(log_payloads)
            for sent, received in zip(log_payloads, received_payloads):
                assert sent["service"] == received["service"]
                assert sent["level"] == received["level"]
                assert sent["message"] == received["message"]
                assert sent["metadata"] == received["metadata"]

    @pytest.mark.asyncio
    async def test_create_log_trigger_alert(self, async_client):
        """Test log creation that triggers an alert when threshold is reached."""

        fake_metric = Mock()
        fake_metric.count = 5
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = fake_metric
        mock_session = AsyncMock()
        mock_session.execute.return_value = mock_result
        mock_cm = AsyncMock()
        mock_cm.__aenter__.return_value = mock_session
        mock_cm.__aexit__.return_value = None
        
        with patch("backend.app.main.AsyncSessionLocal", return_value=mock_cm), \
            patch("backend.app.main.process_log_task") as mock_task:
            mock_task.delay.return_value = type("MockTask", (), {"id": "test-task-id-123"})()

            log_data = {
                "service": "test-service",
                "level": "ERROR",
                "message": "Test error",
                "timestamp": "2024-01-15T12:00:00",
                "metadata": {"user_id": 123},
            }

            response = await async_client.post("/logs/", json=log_data)

            assert response.status_code == 200
            data = response.json()

            assert "ALERTA:" in data["alert"]
            assert "5 ocorrências" in data["alert"]
            assert "ERROR" in data["alert"]
            assert "test-service" in data["alert"]

    @pytest.mark.asyncio
    async def test_create_log_invalid_data(self, async_client):
        """Test log creation with invalid data."""
        invalid_data = {
            "service": "",
            "level": "INVALID_LEVEL",
            "message": "",
            "timestamp": "invalid-timestamp",
        }

        response = await async_client.post("/logs/", json=invalid_data)
        assert response.status_code == 422 


class TestGetTaskStatusEndpoint:
    """Test cases for the get task status endpoint."""

    def test_get_task_status_success(self, client, mock_async_result):
        """Test successful task status retrieval."""
        response = client.get("/tasks/test-task-id-123")

        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "test-task-id-123"
        assert data["status"] == "SUCCESS"
        assert data["result"] == {"processed": True}