from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.audit import record_audit
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.schemas.common import TokenOut, UserCreate, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/bootstrap", response_model=UserOut)
def bootstrap_admin(payload: UserCreate, db: Session = Depends(get_db)):
    """Create first admin only if no users exist. Disable/remove in production hardening."""
    if db.query(User).count() > 0:
        raise HTTPException(status_code=403, detail="Bootstrap disabled: users already exist")
    user = User(
        email=payload.email.lower(),
        full_name=payload.full_name,
        hashed_password=get_password_hash(payload.password),
        role="admin",
        mfa_enabled=False,  # Require MFA setup after bootstrap in production
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    record_audit(db, action="auth.bootstrap", actor_user_id=user.id, actor_email=user.email, resource_type="user", resource_id=user.id)
    return user


@router.post("/login", response_model=TokenOut)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form.username.lower()).first()
    if not user or not verify_password(form.password, user.hashed_password):
        record_audit(db, action="auth.login_failed", actor_email=form.username, outcome="failure")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=401, detail="Inactive user")
    # If MFA enabled, a real implementation would return mfa_required and issue a partial session.
    token = create_access_token(str(user.id), {"role": user.role})
    record_audit(db, action="auth.login", actor_user_id=user.id, actor_email=user.email, resource_type="user", resource_id=user.id)
    return TokenOut(access_token=token, mfa_required=False)
