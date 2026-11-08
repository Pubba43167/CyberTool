from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.connectors.nmap_connector import NmapConnector
from app.core.audit import record_audit
from app.models.asset import Asset
from app.models.enums import CRITICALITY_WEIGHT, Criticality, ScanStatus
from app.models.finding import Finding
from app.models.scan import Scan

CONNECTORS = {
    "nmap": NmapConnector(),
}


def execute_scan(db: Session, scan_id: UUID) -> Scan:
    scan = db.get(Scan, scan_id)
    if not scan:
        raise ValueError("Scan not found")
    if not scan.authorization_verified:
        # Defense in depth: never execute a scan without recorded server-side authorization.
        scan.status = ScanStatus.failed.value
        scan.error_message = "Execution blocked: authorization was not verified."
        db.commit()
        record_audit(db, action="scan.blocked", resource_type="scan", resource_id=scan.id, engagement_id=scan.engagement_id, target=str(scan.asset_id), outcome="failure")
        return scan
    asset = db.get(Asset, scan.asset_id)
    target = asset.target if asset else ""
    connector = CONNECTORS.get((scan.connector or "nmap").lower())
    if not connector:
        scan.status = ScanStatus.failed.value
        scan.error_message = f"Unsupported connector: {scan.connector}"
        db.commit()
        return scan
    scan.status = ScanStatus.running.value
    scan.started_at = datetime.now(timezone.utc)
    db.commit()
    try:
        raw = connector.run(target, scan.parameters)
        scan.raw_output = raw
        # Normalize findings
        for fd in connector.normalize_findings(raw, engagement_id=str(scan.engagement_id), asset_id=str(scan.asset_id), scan_id=str(scan.id)):
            sev = fd.get("severity")
            cvss = fd.get("cvss_score")
            risk = None
            if cvss is not None and asset:
                weight = CRITICALITY_WEIGHT.get(Criticality(asset.criticality), 1.0)
                risk = round(float(cvss) * weight, 2)
            finding = Finding(
                engagement_id=scan.engagement_id,
                asset_id=scan.asset_id,
                scan_id=scan.id,
                title=fd["title"],
                description=fd.get("description"),
                severity=sev or "INFO",
                status=fd.get("status", "OPEN"),
                cve_ids=fd.get("cve_ids"),
                cwe_ids=fd.get("cwe_ids"),
                cvss_vector=fd.get("cvss_vector"),
                cvss_score=cvss,
                risk_score=risk,
                evidence=fd.get("evidence"),
                remediation=fd.get("remediation"),
                connector=fd.get("connector", connector.name),
                dedupe_key=fd.get("dedupe_key"),
                raw=fd.get("raw"),
            )
            db.add(finding)
        if asset:
            asset.last_scanned_at = datetime.now(timezone.utc)
        scan.status = ScanStatus.completed.value
        scan.completed_at = datetime.now(timezone.utc)
        record_audit(db, action="scan.completed", resource_type="scan", resource_id=scan.id, engagement_id=scan.engagement_id, target=target)
    except Exception as e:
        scan.status = ScanStatus.failed.value
        scan.error_message = str(e)
        scan.completed_at = datetime.now(timezone.utc)
        record_audit(db, action="scan.failed", resource_type="scan", resource_id=scan.id, engagement_id=scan.engagement_id, target=target, outcome="failure", details={"error": str(e)})
    db.commit()
    db.refresh(scan)
    return scan
