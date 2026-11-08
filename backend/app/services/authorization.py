"""Server-side authorization gate. This module MUST be used for every scan launch.
No scan may run unless engagement is AUTHORIZED and target is within declared scope.
"""
from __future__ import annotations

import ipaddress
from urllib.parse import urlparse
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.engagement import Engagement, EngagementScopeTarget
from app.models.enums import EngagementStatus


class AuthorizationGateError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


def _normalize_target(value: str) -> str:
    v = (value or "").strip().lower()
    if "://" in v:
        p = urlparse(v)
        return (p.hostname or v).lower()
    return v.split("/")[0].split(":")[0]


def _target_matches_scope(target: str, scope: EngagementScopeTarget) -> bool:
    t = _normalize_target(target)
    s = scope.target_value.strip().lower()
    st = (scope.target_type or "").lower()

    if st == "asset_id":
        return target == scope.target_value
    if st in ("domain", "host"):
        s_norm = _normalize_target(s)
        return t == s_norm or t.endswith("." + s_norm)
    if st == "url":
        return _normalize_target(target) == _normalize_target(s)
    if st in ("ip", "cidr"):
        try:
            tip = ipaddress.ip_address(_normalize_target(target))
            if "/" in s:
                return tip in ipaddress.ip_network(s, strict=False)
            return tip == ipaddress.ip_address(s)
        except ValueError:
            return _normalize_target(target) == _normalize_target(s)
    # fallback: normalized equality
    return _normalize_target(target) == _normalize_target(s)


def require_authorized_scan(db: Session, *, engagement_id: UUID, target: str) -> dict:
    """Non-bypassable server-side gate. Raises AuthorizationGateError if not allowed."""
    engagement = db.get(Engagement, engagement_id)
    if not engagement:
        raise AuthorizationGateError("Engagement not found.")
    if engagement.status != EngagementStatus.authorized.value:
        raise AuthorizationGateError(
            f"Scan blocked: engagement status is '{engagement.status}', must be 'AUTHORIZED' with a signed authorization record."
        )
    if not engagement.authorization_document_path and not engagement.signed_off_by:
        raise AuthorizationGateError(
            "Scan blocked: engagement has no authorization document/sign-off record."
        )
    scopes = (
        db.query(EngagementScopeTarget)
        .filter(EngagementScopeTarget.engagement_id == engagement_id)
        .all()
    )
    if not scopes:
        raise AuthorizationGateError("Scan blocked: engagement has no declared scope targets.")
    if not any(_target_matches_scope(target, s) for s in scopes):
        raise AuthorizationGateError(
            f"Scan blocked: target '{target}' is not inside the engagement's declared scope."
        )
    return {
        "engagement_id": str(engagement_id),
        "engagement_status": engagement.status,
        "target": target,
        "authorized": True,
        "signed_off_by": engagement.signed_off_by,
    }
