from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_roles
from app.core.audit import record_audit
from app.models.asset import Asset
from app.models.enums import Role
from app.models.user import User
from app.schemas.common import AssetCreate, AssetOut

router = APIRouter(prefix="/assets", tags=["assets"])


@router.post("", response_model=AssetOut)
def create_asset(
    payload: AssetCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(Role.admin, Role.lead_pentester, Role.analyst)),
):
    asset = Asset(**payload.model_dump())
    db.add(asset)
    db.commit()
    db.refresh(asset)
    record_audit(db, action="asset.create", actor_user_id=user.id, actor_email=user.email, resource_type="asset", resource_id=asset.id, engagement_id=asset.engagement_id, target=asset.target)
    return asset


@router.get("", response_model=list[AssetOut])
def list_assets(engagement_id: UUID | None = None, db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    q = db.query(Asset)
    if engagement_id:
        q = q.filter(Asset.engagement_id == engagement_id)
    return q.order_by(Asset.created_at.desc()).all()


@router.get("/{asset_id}", response_model=AssetOut)
def get_asset(asset_id: UUID, db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    a = db.get(Asset, asset_id)
    if not a:
        raise HTTPException(status_code=404, detail="Asset not found")
    return a
