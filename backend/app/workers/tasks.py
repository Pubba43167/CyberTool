from uuid import UUID

from app.db.session import SessionLocal
from app.services.scan_service import execute_scan
from app.workers.celery_app import celery_app


@celery_app.task(name="scans.execute", bind=True, max_retries=1)
def execute_scan_task(self, scan_id: str):
    db = SessionLocal()
    try:
        return str(execute_scan(db, UUID(scan_id)).id)
    finally:
        db.close()
