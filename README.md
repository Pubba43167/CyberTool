# SentinelForge

SentinelForge is a scaffold for an authorized cyber security vulnerability assessment and penetration testing orchestration platform.

## What's included
- **Backend (FastAPI, Python 3.12):** core models (users, engagements, assets, scans, findings, reports, audit logs), JWT/RBAC scaffolding, mandatory-MFA hooks, server-side authorization gate, engagement/asset/scan APIs, Nmap connector PoC, Celery/Redis task scaffolding, reporting engine foundations (Jinja/WeasyPrint/python-docx hooks), Alembic migrations.
- **Infra:** Docker Compose for Postgres, Redis, API, worker, frontend (optional ZAP notes).
- **Frontend scaffold:** Vite + React + TypeScript + Tailwind starting point (SOC dark theme tokens).
- **Docs:** setup and scanner integration notes.

## Key safety control
Scan launches are blocked server-side unless the engagement is `AUTHORIZED`, has sign-off/authorization context, and the target is inside declared scope (`app/services/authorization.py`). Every scan stores authorization verification evidence.

## Start here
See [`docs/setup.md`](docs/setup.md) and [`sentinelforge_prompt.md`](sentinelforge_prompt.md).

> Use only on systems you own or have explicit written permission to test.
