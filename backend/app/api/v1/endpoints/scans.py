from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_roles
from app.core.audit import record_audit
from app.models.asset import Asset
from app.models.enums import Role, ScanStatus
from app.models.scan import Scan
from app.models.user import User
from app.schemas.common import ScanLaunch, ScanOut
from app.services.authorization import require_authorized_scan
from app.services.scan_service import execute_scan

router = APIRouter(prefix="/scans", tags=["scans"])


@router.post("/launch", response_model=ScanOut)
def launch_scan(
    payload: ScanLaunch,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(Role.admin, Role.lead_pentester, Role.analyst)),
):
    asset = db.get(Asset, payload.asset_id)
    if not asset or asset.engagement_id != payload.engagement_id:
        raise HTTPException(status_code=404, detail="Asset not found in engagement")
    # HARD GATE (server-side, non-bypassable): must be authorized and in scope.
    auth_ctx = require_authorized_scan(db, engagement_id=payload.engagement_id, target=asset.target)
    scan = Scan(
        engagement_id=payload.engagement_id,
        asset_id=payload.asset_id,
        profile_id=payload.profile_id,
        status=ScanStatus.queued.value,
        requested_by_id=user.id,
        authorization_verified=True,
        authorization_context=auth_ctx,
        connector=payload.connector,
        parameters=payload.parameters,
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)
    record_audit(
        db,
        action="scan.launch",
        actor_user_id=user.id,
        actor_email=user.email,
        resource_type="scan",
        resource_id=scan.id,
        engagement_id=scan.engagement_id,
        target=asset.target,
        details={"connector": payload.connector, "authorization_verified": True},
    )
    # PoC: execute in background thread. Production should dispatch to Celery.
    background_tasks.add_task(_run_scan_task, scan.id)
    return scan


def _run_scan_task(scan_id: UUID) -> None:
    from app.db.session import SessionLocal
    db = SessionLocal()
    try:
        execute_scan(db, scan_id)
    finally:
        db.close()


@router.get("", response_model=list[ScanOut])
def list_scans(engagement_id: UUID | None = None, db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    q = db.query(Scan)
    if engagement_id:
        q = q.filter(Scan.engagement_id == engagement_id)
    return q.order_by(Scan.queued_at.desc()).all()


@router.get("/{scan_id}", response_model=ScanOut)
def get_scan(scan_id: UUID, db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    s = db.get(Scan, scan_id)
    if not s:
        raise HTTPException(status_code=404, detail="Scan not found")
    return s
