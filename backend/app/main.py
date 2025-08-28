# main.py
from fastapi import FastAPI, HTTPException, Query
from .schemas import LogCreate
from .tasks import process_log_task, truncate_minute
from celery.result import AsyncResult
from .celery_app import celery_app
from typing import Optional, List
from .database import AsyncSessionLocal
from .models import LogMetric
from datetime import datetime
from sqlalchemy.future import select

app = FastAPI(title="Log Analytics")

ALERT_THRESHOLD = 5

@app.post("/logs/")
async def create_log(log: LogCreate):
    log_dict = log.model_dump()
    try:
        # Envia para processamento assíncrono
        task = process_log_task.delay(log_dict)

        # Calcula timestamp truncado para o mesmo minuto
        log_ts = log_dict["timestamp"]
        interval_start = truncate_minute(log_ts)

        # Consulta count atual do mesmo service e level
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(LogMetric)
                .filter(
                    LogMetric.service == log_dict["service"],
                    LogMetric.level == log_dict["level"],
                    LogMetric.timestamp == interval_start
                )
            )
            metric = result.scalar_one_or_none()
            current_count = metric.count if metric else 0

        alert_msg = None
        if current_count >= ALERT_THRESHOLD:
            alert_msg = f"ALERTA: {current_count} ocorrências do nível {log_dict['level']} no serviço {log_dict['service']}"

        return {
            "message": "Log recebido e processando.",
            "task_id": task.id,
            "current_count": current_count,
            "alert": alert_msg
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tasks/{task_id}")
def get_task_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result,
    }


@app.get("/logs/service/{service_name}")
async def get_logs_by_service(service_name: str, limit: int = 100):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(LogMetric)
            .filter(LogMetric.service == service_name)
            .order_by(LogMetric.timestamp.desc())
            .limit(limit)
        )
        logs = result.scalars().all()
        return [
            {"service": l.service, "level": l.level, "count": l.count, "timestamp": l.timestamp.isoformat()}
            for l in logs
        ]


@app.get("/logs/level/{level_name}")
async def get_logs_by_level(level_name: str, limit: int = 100):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(LogMetric)
            .filter(LogMetric.level == level_name)
            .order_by(LogMetric.timestamp.desc())
            .limit(limit)
        )
        logs = result.scalars().all()
        return [
            {
                "service": l.service,
                "level": l.level,
                "count": l.count,
                "timestamp": l.timestamp.isoformat(),
            }
            for l in logs
        ]


@app.get("/metrics/service/{service_name}")
async def get_metrics_by_service(
    service_name: str,
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
):
    async with AsyncSessionLocal() as session:
        query = select(LogMetric).filter(LogMetric.service == service_name)
        if start:
            query = query.filter(LogMetric.timestamp >= start)
        if end:
            query = query.filter(LogMetric.timestamp <= end)
        
        result = await session.execute(query)
        logs = result.scalars().all()

        metrics = {}
        for l in logs:
            metrics[l.level] = metrics.get(l.level, 0) + l.count

        return {"service": service_name, "metrics": metrics}



@app.get("/metrics/level/{level_name}")
async def get_metrics_by_level(
    level_name: str,
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
):
    async with AsyncSessionLocal() as session:
        query = select(LogMetric).filter(LogMetric.level == level_name)
        if start:
            query = query.filter(LogMetric.timestamp >= start)
        if end:
            query = query.filter(LogMetric.timestamp <= end)
            
        result = await session.execute(query)
        logs = result.scalars().all()

        metrics = {}
        for l in logs:
            metrics[l.service] = metrics.get(l.service, 0) + l.count

        return {"level": level_name, "metrics": metrics}


@app.get("/alerts/")
async def get_alerts(
    service: str = None,
    level: str = None,
    start: datetime = Query(None),
    end: datetime = Query(None),
    limit: int = 100
):
    async with AsyncSessionLocal() as session:
        query = select(LogMetric).where(LogMetric.count >= ALERT_THRESHOLD)

        if service:
            query = query.where(LogMetric.service == service)
        if level:
            query = query.where(LogMetric.level == level)
        if start:
            query = query.where(LogMetric.timestamp >= start)
        if end:
            query = query.where(LogMetric.timestamp <= end)

        query = query.order_by(LogMetric.timestamp.desc()).limit(limit)
        result = await session.execute(query)
        metrics = result.scalars().all()

        alerts = []
        for m in metrics:
            alerts.append({
                "service": m.service,
                "level": m.level,
                "count": m.count,
                "timestamp": m.timestamp,
                "alert": f"ALERT: {m.count} occurrences of {m.level} in service {m.service} at {m.timestamp}"
            })

        return alerts
    

@app.get("/")
async def root():
    return {"message": "API de Logs funcionando!"}
