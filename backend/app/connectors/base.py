from abc import ABC, abstractmethod
from typing import Any


class ConnectorResult(dict):
    """Normalized-ish container returned by connectors."""
    pass


class BaseConnector(ABC):
    name: str = "base"

    @abstractmethod
    def run(self, target: str, parameters: dict[str, Any] | None = None) -> ConnectorResult:
        raise NotImplementedError

    def normalize_findings(self, raw: ConnectorResult, *, engagement_id: str, asset_id: str, scan_id: str) -> list[dict[str, Any]]:
        """Convert raw connector output into normalized finding dicts."""
        return []
