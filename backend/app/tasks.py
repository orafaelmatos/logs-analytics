# tasks.py
from .celery_app import celery_app
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from pymongo import MongoClient
from .models import LogMetric
from datetime import datetime


# PostgreSQL síncrono
engine = create_engine("postgresql://postgres:postgres@postgres:5432/logs")
SessionLocal = sessionmaker(bind=engine)

# MongoDB síncrono
mongo_client = MongoClient("mongodb://mongo:27017")
mongo_db = mongo_client.logs

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
    
    session = SessionLocal()
    try:
        metric = (
            session.query(LogMetric)
            .filter_by(
                service=log_data["service"],
                level=log_data["level"],
                timestamp=interval_start
            )
            .first()
        )

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

        session.commit()

    finally:
        session.close()

    return {
        "mongo_inserted": True,
        "postgres_updated": True,
        "service": log_data["service"],
        "level": log_data["level"],
    }