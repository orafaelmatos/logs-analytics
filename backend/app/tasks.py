# tasks.py
from .celery_app import celery_app
from .database import mongo_db, SessionLocal
from .models import LogMetric
from datetime import datetime
import asyncio
from sqlalchemy.future import select
from zoneinfo import ZoneInfo



BRAZIL_TZ = ZoneInfo("America/Sao_Paulo")

def truncate_minute(dt: datetime) -> datetime:
    """
    Truncate datetime to the start of the minute, convert to Brazil timezone, 
    and return **naive datetime** suitable for PostgreSQL TIMESTAMP WITHOUT TIME ZONE.
    """
    BRAZIL_TZ = ZoneInfo("America/Sao_Paulo")

    # Convert to Brazil timezone
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=BRAZIL_TZ)
    else:
        dt = dt.astimezone(BRAZIL_TZ)
    
    # Remove tzinfo to make naive
    return dt.replace(second=0, microsecond=0, tzinfo=None)


@celery_app.task(name="app.tasks.process_log_task")
def process_log_task(log_data: dict):
    # MongoDB insert
    mongo_db.logs.insert_one(log_data)

    # PostgreSQL metrics
    log_ts = log_data["timestamp"]
    interval_start = truncate_minute(log_ts)

    session = SessionLocal()
    try:
        metric = session.query(LogMetric).filter_by(
            service=log_data["service"],
            level=log_data["level"],
            timestamp=interval_start
        ).one_or_none()

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