from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import FindingSeverity, FindingStatus


class Finding(Base):
    __tablename__ = "findings"

    id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    engagement_id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), ForeignKey("engagements.id", ondelete="CASCADE"), nullable=False, index=True)
    asset_id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    scan_id: Mapped[uuid4 | None] = mapped_column(UUID(as_uuid=True), ForeignKey("scans.id", ondelete="SET NULL"), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default=FindingSeverity.info.value, index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default=FindingStatus.open.value, index=True)
    cve_ids: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    cwe_ids: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    cvss_vector: Mapped[str | None] = mapped_column(String(200), nullable=True)
    cvss_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)  # CVSS * criticality weight
    evidence: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    remediation: Mapped[str | None] = mapped_column(Text, nullable=True)
    remediation_effort: Mapped[str | None] = mapped_column(String(50), nullable=True)
    connector: Mapped[str | None] = mapped_column(String(100), nullable=True)
    dedupe_key: Mapped[str | None] = mapped_column(String(512), nullable=True, index=True)
    raw: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    asset: Mapped["Asset"] = relationship(back_populates="findings")
    scan: Mapped["Scan | None"] = relationship(back_populates="findings")
