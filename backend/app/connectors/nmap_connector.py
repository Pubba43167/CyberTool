import shutil
from typing import Any

from app.connectors.base import BaseConnector, ConnectorResult


class NmapConnector(BaseConnector):
    name = "nmap"

    def run(self, target: str, parameters: dict[str, Any] | None = None) -> ConnectorResult:
        params = parameters or {}
        args = params.get("arguments", "-sV --top-ports 100")
        if not shutil.which("nmap"):
            return ConnectorResult(
                ok=False,
                connector=self.name,
                target=target,
                error="nmap binary not found on PATH. Install Nmap or run via the provided container/orchestration.",
                raw={},
            )
        try:
            import nmap  # python-nmap
        except Exception as e:  # pragma: no cover
            return ConnectorResult(ok=False, connector=self.name, target=target, error=f"python-nmap unavailable: {e}", raw={})
        scanner = nmap.PortScanner()
        scan_data = scanner.scan(hosts=target, arguments=args)
        return ConnectorResult(ok=True, connector=self.name, target=target, arguments=args, raw=scan_data)

    def normalize_findings(self, raw: ConnectorResult, *, engagement_id: str, asset_id: str, scan_id: str) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []
        if not raw.get("ok"):
            return [{
                "engagement_id": engagement_id,
                "asset_id": asset_id,
                "scan_id": scan_id,
                "title": f"Nmap scan error: {raw.get('target')}",
                "description": raw.get("error"),
                "severity": "INFO",
                "status": "OPEN",
                "connector": self.name,
                "evidence": {"target": raw.get("target")},
                "dedupe_key": f"nmap:error:{asset_id}:{raw.get('error','')[:120]}",
            }]
        scan = (raw.get("raw") or {}).get("scan", {})
        for host, hostdata in scan.items():
            for proto, ports in (hostdata.get("tcp", {}) or hostdata.get("udp", {}) and {} ).items() if False else []:
                pass
            # python-nmap structure: scan[host]['tcp'/'udp'][port]
            for proto in ("tcp", "udp"):
                for port, pdata in (hostdata.get(proto) or {}).items():
                    state = pdata.get("state")
                    service = pdata.get("name") or "unknown"
                    product = " ".join(filter(None, [pdata.get("product"), pdata.get("version")])).strip()
                    title = f"Open {proto.upper()} port {port}/{service} on {host}"
                    sev = "INFO"
                    if state == "open" and port in (23, 21, 445, 3389, 5900):
                        sev = "MEDIUM"
                    if state == "open" and port in (1433, 3306, 5432, 6379, 27017):
                        sev = "HIGH"
                    findings.append({
                        "engagement_id": engagement_id,
                        "asset_id": asset_id,
                        "scan_id": scan_id,
                        "title": title,
                        "description": f"Port {port}/{proto} is {state}. Service: {service}. {('Product: ' + product) if product else ''}".strip(),
                        "severity": sev,
                        "status": "OPEN",
                        "connector": self.name,
                        "evidence": {"host": host, "port": port, "protocol": proto, "service": pdata},
                        "remediation": "Restrict exposure with firewall rules, disable unused services, enforce authentication/encryption, and patch exposed services.",
                        "dedupe_key": f"nmap:{asset_id}:{host}:{proto}:{port}:{state}",
                        "raw": pdata,
                    })
        if not findings:
            findings.append({
                "engagement_id": engagement_id,
                "asset_id": asset_id,
                "scan_id": scan_id,
                "title": f"Nmap completed for {raw.get('target')} (no open ports in scanned range)",
                "description": "No findings were produced from the scanned port range/arguments.",
                "severity": "INFO",
                "status": "OPEN",
                "connector": self.name,
                "evidence": {"target": raw.get("target"), "arguments": raw.get("arguments")},
                "dedupe_key": f"nmap:none:{asset_id}:{raw.get('target')}",
            })
        return findings
