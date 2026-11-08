from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import AssetType, Criticality, Environment


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    engagement_id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), ForeignKey("engagements.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    asset_type: Mapped[str] = mapped_column(String(50), nullable=False, default=AssetType.web_app.value)
    target: Mapped[str] = mapped_column(String(1024), nullable=False)  # host, URL, IP, identifier
    criticality: Mapped[str] = mapped_column(String(20), nullable=False, default=Criticality.medium.value)
    environment: Mapped[str] = mapped_column(String(20), nullable=False, default=Environment.development.value)
    owner: Mapped[str | None] = mapped_column(String(200), nullable=True)
    tags: Mapped[dict | list | None] = mapped_column(JSONB, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_scanned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    current_risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    engagement: Mapped["Engagement"] = relationship(back_populates="assets")
    scans: Mapped[list["Scan"]] = relationship(back_populates="asset")
    findings: Mapped[list["Finding"]] = relationship(back_populates="asset")
