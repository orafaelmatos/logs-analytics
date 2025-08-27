import pytest
from datetime import datetime, timedelta
from app.schemas import LogCreate

ALERT_THRESHOLD = 5

@pytest.mark.asyncio
async def test_root(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "API de Logs funcionando!"}

@pytest.mark.asyncio
async def test_create_log(client):
    log = {
        "service": "test_service",
        "level": "ERROR",
        "message": "Teste de log",
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": {"user_id": 1}
    }
    response = await client.post("/logs/", json=log)
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert "current_count" in data
    assert data["current_count"] >= 0

@pytest.mark.asyncio
async def test_get_logs_by_service(client):
    response = await client.get("/logs/service/test_service")
    assert response.status_code == 200
    logs = response.json()
    assert isinstance(logs, list)
    if logs:
        assert logs[0]["service"] == "test_service"

@pytest.mark.asyncio
async def test_get_metrics_by_service(client):
    response = await client.get("/metrics/service/test_service")
    assert response.status_code == 200
    metrics = response.json()
    assert "service" in metrics
    assert metrics["service"] == "test_service"
    assert "metrics" in metrics

@pytest.mark.asyncio
async def test_alert_endpoint(client):
    # Insere logs acima do ALERT_THRESHOLD
    for _ in range(ALERT_THRESHOLD + 1):
        log = {
            "service": "alert_service",
            "level": "ERROR",
            "message": "Teste alerta",
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {}
        }
        await client.post("/logs/", json=log)

    response = await client.get("/alerts/?service=alert_service&level=ERROR")
    assert response.status_code == 200
    alerts = response.json()
    assert isinstance(alerts, list)
    assert any(a["count"] >= ALERT_THRESHOLD for a in alerts)
