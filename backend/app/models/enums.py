import enum


class Role(str, enum.Enum):
    admin = "admin"
    lead_pentester = "lead_pentester"
    analyst = "analyst"
    client_read_only = "client_read_only"


class EngagementStatus(str, enum.Enum):
    draft = "DRAFT"
    pending_authorization = "PENDING_AUTHORIZATION"
    authorized = "AUTHORIZED"
    in_progress = "IN_PROGRESS"
    completed = "COMPLETED"
    archived = "ARCHIVED"


class AssetType(str, enum.Enum):
    windows_app = "WINDOWS_APP"
    web_app = "WEB_APP"
    database_server = "DATABASE_SERVER"
    windows_server = "WINDOWS_SERVER"
    linux_server = "LINUX_SERVER"
    vm_cloud_instance = "VM_CLOUD_INSTANCE"
    api_backend_service = "API_BACKEND_SERVICE"


class Environment(str, enum.Enum):
    production = "prod"
    staging = "staging"
    development = "dev"


class Criticality(str, enum.Enum):
    critical = "CRITICAL"
    high = "HIGH"
    medium = "MEDIUM"
    low = "LOW"


CRITICALITY_WEIGHT = {
    Criticality.critical: 1.5,
    Criticality.high: 1.2,
    Criticality.medium: 1.0,
    Criticality.low: 0.8,
}


class ScanStatus(str, enum.Enum):
    queued = "QUEUED"
    running = "RUNNING"
    completed = "COMPLETED"
    failed = "FAILED"
    cancelled = "CANCELLED"


class FindingSeverity(str, enum.Enum):
    critical = "CRITICAL"
    high = "HIGH"
    medium = "MEDIUM"
    low = "LOW"
    info = "INFO"


class FindingStatus(str, enum.Enum):
    open = "OPEN"
    assigned = "ASSIGNED"
    in_remediation = "IN_REMEDIATION"
    pending_retest = "PENDING_RETEST"
    verified_closed = "VERIFIED_CLOSED"
    accepted_risk = "ACCEPTED_RISK"


class ReportType(str, enum.Enum):
    penetration_test = "PENETRATION_TEST"
    vulnerability_assessment = "VULNERABILITY_ASSESSMENT"
    soc = "SOC"
    remediation_suggestions = "REMEDIATION_SUGGESTIONS"
