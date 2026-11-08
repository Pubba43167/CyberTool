from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "SentinelForge"
    environment: str = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    # Security
    secret_key: str = "CHANGE-ME-IN-PRODUCTION"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    mfa_issuer_name: str = "SentinelForge"
    secrets_encryption_key: str = ""  # Fernet key (base64). Required in production.

    # Database
    database_url: str = "postgresql+psycopg2://sentinel:sentinel@postgres:5432/sentinelforge"

    # Redis / Celery
    redis_url: str = "redis://redis:6379/0"
    celery_broker_url: str = "redis://redis:6379/1"
    celery_result_backend: str = "redis://redis:6379/2"

    # Scanner/runtime controls
    max_concurrent_scans: int = 2
    scan_rate_limit_per_minute: int = 30

    # NVD enrichment
    nvd_api_base: str = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    nvd_api_key: str = ""


settings = Settings()
