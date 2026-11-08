# SentinelForge — Build Prompt

Paste everything below into Claude Code (or another AI coding assistant) to build the platform.

---

```
Build "SentinelForge" — a full-stack Cyber Security Vulnerability 
Assessment & Penetration Testing Orchestration Platform.

=====================================================================
CORE CONCEPT
=====================================================================
SentinelForge is NOT a raw exploit engine. It is an orchestration, 
asset-management, and reporting platform that:
1. Manages scan targets (Windows apps, web apps, DBs, servers, VMs/
   cloud, APIs, backends) as "Assets" grouped into "Engagements"
2. Enforces an Authorization Gate — no scan can run against a target 
   until a signed scope document / authorization record exists for it
3. Orchestrates established, industry-standard open-source scanners 
   via their APIs/CLIs (Nmap, OpenVAS/Greenbone GVM, OWASP ZAP, 
   Nikto, Trivy, testssl.sh, Nuclei) rather than reimplementing 
   exploits
4. Normalizes all findings into a unified vulnerability schema 
   (CVE/CVSS/CWE mapped)
5. Generates polished, client-ready reports: Penetration Test Report, 
   Vulnerability Assessment Report, SOC/Executive Report, and 
   Remediation Suggestions — as PDF/HTML/DOCX
6. Tracks remediation lifecycle (open → in progress → verified fixed)

=====================================================================
TECH STACK (chosen for this use case)
=====================================================================
- Backend: Python 3.12 + FastAPI (async, great for orchestrating 
  long-running scan jobs; huge security/OSINT library ecosystem)
- Task Queue: Celery + Redis (scans are long-running, need to be 
  queued, retried, cancelled)
- Database: PostgreSQL 16 (relational integrity for 
  engagements/assets/findings; JSONB columns for raw scanner output)
- ORM: SQLAlchemy 2.0 + Alembic migrations
- Frontend: React 18 + TypeScript + Vite + Tailwind CSS + shadcn/ui
  - Dark, "SOC dashboard" cyber theme (see Design System below)
  - Recharts for risk trend graphs / severity heatmaps
- Auth: JWT + RBAC (roles: Admin, Lead Pentester, Analyst, 
  Client-Read-Only) + mandatory MFA (TOTP)
- Report generation: WeasyPrint (HTML→PDF) + Jinja2 templates; 
  python-docx for Word export
- Scanner integrations (each as a pluggable "Connector" module):
  - Nmap (python-nmap) — network/port/service discovery
  - OpenVAS/Greenbone GVM (gvm-tools / python-gvm) — full CVE-based 
    vulnerability scanning for hosts/servers
  - OWASP ZAP (zaproxy Python API) — web app DAST
  - Nuclei — fast template-based scanning (CVEs, misconfig, exposed 
    panels)
  - Nikto — web server misconfig scanning
  - testssl.sh — TLS/SSL configuration auditing
  - Trivy — container/VM image & IaC scanning (cloud workloads)
  - SQL-specific: custom read-only checks module (see "Database 
    Server Module" below) using native drivers (pyodbc for SQL 
    Server, psycopg2 for Postgres)
  - Cloud posture: ScoutSuite or Prowler wrapper (AWS/Azure/GCP 
    misconfiguration scanning) for VM/Cloud Server assets
- CVE/CVSS enrichment: NVD API v2.0 (live lookups + nightly local 
  mirror cache in Postgres so enrichment works offline)
- Containerization: Docker Compose (API, worker, Postgres, Redis, 
  frontend, + optional OpenVAS/ZAP containers)

=====================================================================
MODULES / FEATURES
=====================================================================

1. ENGAGEMENT & AUTHORIZATION MODULE
   - Create "Engagement" (client name, scope, start/end dates, 
     authorization document upload, signed-off-by field)
   - Hard gate: scan launch button is disabled server-side (not just 
     UI) unless engagement.status == "AUTHORIZED" and target IP/
     domain/asset is inside the declared scope list
   - Full audit log of who launched what scan against what, when

2. ASSET INVENTORY MODULE
   - Asset types: Windows App, Web App, Database Server, Windows 
     Server, Linux Server, VM/Cloud Instance (AWS/Azure/GCP tagged), 
     API/Backend Service
   - Each asset: criticality rating, owner, environment 
     (prod/staging/dev), tags, last-scanned date, current risk score

3. SCAN ORCHESTRATION MODULE
   - "Scan Profile" templates: Quick Discovery, Full Vulnerability 
     Scan, Web App DAST, Database Hardening Audit, Cloud Posture 
     Review, API Security Scan
   - Each profile maps to one or more Connector modules above, run 
     via Celery tasks, with live progress streamed to UI (WebSocket)
   - Results land in a normalized `findings` table (see schema)

4. DATABASE SERVER HARDENING MODULE (read-only checks — safe to run
   in production, no exploitation)
   - For SQL Server: xp_cmdshell enabled?, sa account enabled/weak 
     password policy, excessive sysadmin role members, unencrypted 
     connections (no TLS/force encryption), TDE status, linked 
     server config exposure, SQL Server version/patch level vs 
     known CVEs, weak/default accounts, public role permissions 
     audit, backup file permissions
   - For PostgreSQL/MySQL: equivalent CIS-benchmark-style checks
   - Maps every finding to CIS Benchmark control IDs

5. FINDINGS & RISK ENGINE
   - Normalizes every connector's raw output into: title, 
     description, affected asset, CVE ID(s), CVSS v3.1 vector+score, 
     CWE category, evidence, remediation guidance, status
   - Risk score = CVSS base score × asset criticality weight
   - Deduplication across multiple scan runs

6. REPORTING ENGINE (the centerpiece)
   - Report Types:
     a. Penetration Testing Report — exec summary, scope, 
        methodology (PTES/OWASP phases), findings by severity, 
        attack narrative, evidence screenshots, remediation roadmap
     b. Vulnerability Assessment Report — full asset-by-asset finding 
        list, CVSS heatmap, trend vs last scan
     c. SOC Report — ongoing monitoring summary, MTTR metrics, 
        incident correlation, compliance posture (ISO 27001/PCI-DSS/
        SOC 2 control mapping)
     d. AI-assisted Suggestions — for each finding, generate 
        prioritized remediation steps + effort estimate
   - Output formats: PDF (branded, cover page, TOC), HTML (for web 
     portal viewing), DOCX (for client editing)
   - Severity color coding: Critical=#FF1744, High=#FF6D00, 
     Medium=#FFD600, Low=#00E676, Info=#00B8D4

7. REMEDIATION TRACKING
   - Kanban-style board: Open → Assigned → In Remediation → 
     Pending Retest → Verified Closed
   - Re-scan-to-verify workflow (re-runs the specific check, 
     auto-closes finding if resolved)

8. DASHBOARD (Cyber Security Theme — see Design System)
   - Global risk posture gauge, severity distribution donut, 
     top 10 riskiest assets, scan activity timeline, live "SOC feed" 
     of recent findings

=====================================================================
DESIGN SYSTEM — "Cyber SOC" Theme
=====================================================================
- Palette: near-black background (#0A0E14), panel surfaces (#121821), 
  neon-cyan accent (#00F0FF) for primary actions/links, matrix-green 
  (#39FF14) for "healthy/secure" states, alert-red (#FF1744) for 
  critical, amber (#FFB300) for warnings
- Typography: monospace accents for IDs/hashes/CVEs (JetBrains Mono 
  or Fira Code), clean sans-serif for body (Inter)
- Visual motifs: subtle animated grid/circuit-line background on 
  login & dashboard, terminal-style log viewer for live scan output, 
  glowing border on active/running scans, radar-sweep loading 
  animation for scan-in-progress states
- Light mode optional but dark is default — this is a SOC tool, 
  analysts live in it for hours

=====================================================================
NON-FUNCTIONAL REQUIREMENTS
=====================================================================
- Every scan action requires explicit stored authorization (see 
  module 1) — build this as a non-bypassable server-side check, 
  not a UI suggestion
- Full audit trail (who/what/when) on every scan, report export, 
  and credential use
- Secrets (DB creds, cloud API keys for scanning) stored encrypted 
  at rest (Fernet/KMS), never logged in plaintext
- Rate-limit/throttle scan concurrency to avoid accidental DoS of 
  targets
- RBAC enforced at API layer, not just frontend

Build this as a monorepo with /backend, /frontend, /infra 
(docker-compose + Alembic migrations), and a /docs folder with 
setup instructions for standing up OpenVAS/ZAP containers. Start 
by scaffolding the database schema and core FastAPI models, then 
the Engagement/Asset/Auth modules, then one scanner connector 
(Nmap) end-to-end as a proof of concept, then the reporting engine.
```

---

## Related file

The matching PostgreSQL schema (engagements, assets, scans, findings, reports, audit log, seed data) is in `sentinelforge_schema.sql`, shared earlier in this conversation.
