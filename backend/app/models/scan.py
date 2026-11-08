from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import ScanStatus


class ScanProfile(Base):
    __tablename__ = "scan_profiles"

    id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    connectors: Mapped[list | dict] = mapped_column(JSONB, nullable=False, default=list)  # ordered connector configs
    is_builtin: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Scan(Base):
    __tablename__ = "scans"

    id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    engagement_id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), ForeignKey("engagements.id", ondelete="CASCADE"), nullable=False, index=True)
    asset_id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    profile_id: Mapped[uuid4 | None] = mapped_column(UUID(as_uuid=True), ForeignKey("scan_profiles.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default=ScanStatus.queued.value, index=True)
    requested_by_id: Mapped[uuid4 | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    # Server-side authorization evidence
    authorization_verified: Mapped[bool] = mapped_column(default=False, nullable=False)
    authorization_context: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    connector: Mapped[str | None] = mapped_column(String(100), nullable=True)
    parameters: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    raw_output: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    queued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    celery_task_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    asset: Mapped["Asset"] = relationship(back_populates="scans")
    findings: Mapped[list["Finding"]] = relationship(back_populates="scan")
