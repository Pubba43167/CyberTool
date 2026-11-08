from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_roles
from app.core.audit import record_audit
from app.models.engagement import Engagement, EngagementScopeTarget
from app.models.enums import EngagementStatus, Role
from app.models.user import User
from app.schemas.common import EngagementAuthorize, EngagementCreate, EngagementOut

router = APIRouter(prefix="/engagements", tags=["engagements"])


@router.post("", response_model=EngagementOut)
def create_engagement(
    payload: EngagementCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(Role.admin, Role.lead_pentester)),
):
    e = Engagement(**payload.model_dump(), created_by_id=user.id, status=EngagementStatus.draft.value)
    db.add(e)
    db.commit()
    db.refresh(e)
    record_audit(db, action="engagement.create", actor_user_id=user.id, actor_email=user.email, resource_type="engagement", resource_id=e.id, engagement_id=e.id)
    return e


@router.get("", response_model=list[EngagementOut])
def list_engagements(db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    return db.query(Engagement).order_by(Engagement.created_at.desc()).all()


@router.get("/{engagement_id}", response_model=EngagementOut)
def get_engagement(engagement_id: UUID, db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    e = db.get(Engagement, engagement_id)
    if not e:
        raise HTTPException(status_code=404, detail="Engagement not found")
    return e


@router.post("/{engagement_id}/authorize", response_model=EngagementOut)
def authorize_engagement(
    engagement_id: UUID,
    payload: EngagementAuthorize,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(Role.admin, Role.lead_pentester)),
):
    e = db.get(Engagement, engagement_id)
    if not e:
        raise HTTPException(status_code=404, detail="Engagement not found")
    if not payload.signed_off_by:
        raise HTTPException(status_code=400, detail="signed_off_by is required")
    e.authorization_document_path = payload.authorization_document_path
    e.signed_off_by = payload.signed_off_by
    from datetime import datetime, timezone
    e.signed_off_at = datetime.now(timezone.utc)
    e.status = EngagementStatus.authorized.value
    # Replace scope targets
    db.query(EngagementScopeTarget).filter(EngagementScopeTarget.engagement_id == e.id).delete()
    for t in payload.scope_targets:
        db.add(EngagementScopeTarget(engagement_id=e.id, target_type=t.get("target_type", "domain"), target_value=t["target_value"], notes=t.get("notes")))
    db.commit()
    db.refresh(e)
    record_audit(db, action="engagement.authorize", actor_user_id=user.id, actor_email=user.email, resource_type="engagement", resource_id=e.id, engagement_id=e.id, details={"scope_count": len(payload.scope_targets)})
    return e
