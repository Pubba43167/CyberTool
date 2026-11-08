# SentinelForge Setup

## Prerequisites
- Docker + Docker Compose (recommended)
- Python 3.12 (for local backend dev)
- Node.js 20+ (for local frontend dev)
- PostgreSQL 16 and Redis 7 (or use Docker Compose)

## Quick start (Docker Compose)
1. Copy env file:
   ```bash
   cp backend/.env.example backend/.env
   ```
   Set `SECRET_KEY` to a strong random value. In production, set `SECRETS_ENCRYPTION_KEY` (Fernet key).

2. Start services from `infra/`:
   ```bash
   cd infra
   docker compose up --build
   ```

3. Run migrations (in another shell):
   ```bash
   docker compose exec api alembic upgrade head
   ```

4. API: http://localhost:8000 (`/docs` for OpenAPI). Frontend: http://localhost:5173.

## Bootstrap admin
If no users exist:
```bash
curl -X POST http://localhost:8000/api/v1/auth/bootstrap \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","full_name":"Admin","password":"ChangeMe123!","role":"admin"}'
```
Then login via `/api/v1/auth/login` (OAuth2 form: `username`, `password`). **Enable MFA and disable/remove bootstrap in production.**

## Nmap proof-of-concept flow
1. Create engagement (AUTHORIZED requires authorize step).
2. Authorize engagement with `signed_off_by` and `scope_targets` (e.g. `{"target_type":"domain","target_value":"scanme.nmap.org"}` or an approved internal target).
3. Create an asset under the engagement with `target` matching scope.
4. Launch scan (`connector: nmap`). The server enforces the authorization gate; scans outside scope or non-authorized engagements are rejected.
5. Review scan/findings via API (findings endpoints can be extended as needed).

> **Only scan targets you own or have explicit written authorization to test.**

## Optional scanners (containers/integrations)
- **OWASP ZAP**: uncomment the `zap` service in `infra/docker-compose.yml` and configure the ZAP connector to use its API.
- **OpenVAS/Greenbone (GVM)**: Greenbone Community Edition is typically deployed as a dedicated multi-container stack. Run it separately and point the OpenVAS connector at the GMP API with credentials stored encrypted in SentinelForge.
- **Nuclei/Nikto/testssl.sh/Trivy**: add container images or host binaries and implement connectors under `backend/app/connectors/` following `BaseConnector`.

## Security notes
- The authorization gate is enforced server-side in `app/services/authorization.py` and checked on scan launch. Do not bypass it.
- All scan launches, auth events, and key actions should be recorded in `audit_logs`.
- Store secrets encrypted at rest (Fernet/KMS) and never log credentials.
- Apply rate limiting/throttling to avoid accidental target impact.
- Enforce RBAC at the API layer and require MFA for production users.
