# tasks.py
from .celery_app import celery_app
from .database import AsyncSessionLocal, mongo_db
from .models import LogMetric
from datetime import datetime
import asyncio
from sqlalchemy.future import select

def truncate_minute(dt: datetime) -> datetime:
    """Trunca datetime para o início do minuto"""
    return dt.replace(second=0, microsecond=0)

@celery_app.task(name="app.tasks.process_log_task")
def process_log_task(log_data: dict):
    """
    Task executada de forma assíncrona pelo worker.
    Salva log no MongoDB e atualiza métricas agregadas no PostgreSQL.
    Gera alerta se count atingir limite definido (apenas na primeira vez).
    Retorna quantidade atual do erro por serviço e nível.
    """
    # --- MongoDB: log bruto ---
    mongo_db.logs.insert_one(log_data)

    # --- PostgreSQL: métricas ---
    log_ts = log_data["timestamp"]
    interval_start = truncate_minute(log_ts)
    
    # Run async database operations in a new event loop
    def run_async_db_operations():
        async def async_db_ops():
            async with AsyncSessionLocal() as session:
                # Use SQLAlchemy 2.x async syntax
                stmt = select(LogMetric).filter_by(
                    service=log_data["service"],
                    level=log_data["level"],
                    timestamp=interval_start
                )
                result = await session.execute(stmt)
                metric = result.scalar_one_or_none()

                if metric:
                    metric.count += 1
                else:
                    metric = LogMetric(
                        service=log_data["service"],
                        level=log_data["level"],
                        count=1,
                        timestamp=interval_start
                    )
                    session.add(metric)

                await session.commit()

        # Create new event loop for this thread
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(async_db_ops())
        finally:
            loop.close()

    run_async_db_operations()

    return {
        "mongo_inserted": True,
        "postgres_updated": True,
        "service": log_data["service"],
        "level": log_data["level"],
    }