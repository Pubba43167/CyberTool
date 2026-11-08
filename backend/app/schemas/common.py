from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    email: str
    full_name: str
    password: str = Field(min_length=8)
    role: str = "analyst"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    email: str
    full_name: str
    role: str
    is_active: bool
    mfa_enabled: bool


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    mfa_required: bool = False


class EngagementCreate(BaseModel):
    name: str
    client_name: str
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None


class EngagementAuthorize(BaseModel):
    authorization_document_path: str | None = None
    signed_off_by: str
    scope_targets: list[dict[str, Any]] = []  # {target_type, target_value, notes}


class EngagementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    client_name: str
    status: str
    start_date: date | None
    end_date: date | None
    signed_off_by: str | None
    created_at: datetime


class AssetCreate(BaseModel):
    engagement_id: UUID
    name: str
    asset_type: str
    target: str
    criticality: str = "MEDIUM"
    environment: str = "dev"
    owner: str | None = None
    tags: Any = None
    description: str | None = None


class AssetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    engagement_id: UUID
    name: str
    asset_type: str
    target: str
    criticality: str
    environment: str
    current_risk_score: float | None


class ScanLaunch(BaseModel):
    engagement_id: UUID
    asset_id: UUID
    connector: str = "nmap"
    profile_id: UUID | None = None
    parameters: dict[str, Any] = {}


class ScanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    engagement_id: UUID
    asset_id: UUID
    status: str
    connector: str | None
    authorization_verified: bool
    queued_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    error_message: str | None
