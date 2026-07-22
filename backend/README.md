# ChangeFlow — Backend (Flask + SQL Server)

REST API for the Application & Enhancement Request Management System described
in the Application Design Pack (Screen-wise Wireframes, Database Design, Role &
Permission Matrix, Workflow, Dashboard).

## Quick start (local demo, SQLite)

```bash
cd backend
python3 -m venv venv && source venv/bin/activate      # optional but recommended
pip install -r requirements.txt
python utils/seed.py          # creates tables + demo users (SQLite by default)
python app.py                 # runs on http://127.0.0.1:5000
```

Demo logins (password for all: `Passw0rd!`):

| Email | Role |
|---|---|
| admin@demo.com | Admin |
| requester@demo.com | Requester |
| platformowner@demo.com | Platform Owner |
| pgc@demo.com | PGC |
| developer@demo.com | Developer |

## Switching to SQL Server

1. Create the database and tables:
   ```
   sqlcmd -S <server> -i database/schema_sqlserver.sql
   ```
2. Install the ODBC driver on the host OS (Microsoft "ODBC Driver 17/18 for SQL Server").
3. Uncomment `pyodbc` in `requirements.txt` and `pip install -r requirements.txt` again.
4. Set the connection string and re-run the seed script against SQL Server:
   ```bash
   export DATABASE_URL="mssql+pyodbc://<user>:<password>@<server>/AppRequestMgmtDB?driver=ODBC+Driver+17+for+SQL+Server"
   python utils/seed.py
   python app.py
   ```

Because the app uses SQLAlchemy, `models.py` works unchanged against SQLite or
SQL Server — only `DATABASE_URL` changes. Note: `dashboard.py`'s monthly-trend
query uses SQLite's `strftime`; on SQL Server swap it for `FORMAT(CreatedDate,'yyyy-MM')`.

## Folder structure

```
backend/
  app.py                 Flask application factory + blueprint registration
  config.py              Environment-driven configuration
  extensions.py          Shared SQLAlchemy / CORS instances
  models.py              ORM models (mirror database/schema_sqlserver.sql)
  routes/
    auth.py              /api/auth        login, forgot-password, me
    requests.py          /api/requests    Raise Request, My Requests
    approvals.py         /api/approvals   Platform Owner + PGC decisions
    development.py       /api/development Development Tracking
    dashboard.py         /api/dashboard   KPIs + chart data
    reports.py           /api/reports     filtered grid + Excel/PDF export
    admin.py             /api/admin       Platforms / Users / Categories CRUD
    lookups.py           /api/platforms, /api/categories, /api/developers
  utils/
    decorators.py        JWT issue/verify, @token_required, @roles_required
    seed.py               one-shot DB init + demo data
  database/
    schema_sqlserver.sql  DDL (source of truth for table design)
    seed_data.sql          reference-only seed script for SQL Server
```

## Authentication

Stateless JWT. `POST /api/auth/login` returns a token; the frontend sends it as
`Authorization: Bearer <token>` on every subsequent call. Tokens expire after 8
hours (`Config.JWT_EXPIRY`).

## API reference (summary)

| Method & Path | Roles | Purpose |
|---|---|---|
| POST /api/auth/login | any | Authenticate, get JWT |
| POST /api/auth/forgot-password | any | Stub — always returns 200 |
| GET  /api/auth/me | logged in | Current user profile |
| POST /api/requests | Requester, Admin | Raise Request (multipart, supports `attachment`) |
| GET  /api/requests | logged in | My Requests — scoped by role, `?search=&status=` |
| GET  /api/requests/:id | logged in | Full detail incl. approvals + timeline |
| GET  /api/requests/:id/attachment | logged in | Download attachment |
| GET  /api/approvals/platform-owner | Platform Owner, Admin | Pending queue |
| POST /api/approvals/platform-owner/:id | Platform Owner, Admin | `{decision, remarks}` |
| GET  /api/approvals/pgc | PGC, Admin | Pending queue |
| POST /api/approvals/pgc/:id | PGC, Admin | `{decision, remarks}` |
| GET  /api/development | logged in | List (scoped for Developer) |
| PUT  /api/development/:id | Developer, Admin | Update owner/dates/progress/status |
| GET  /api/dashboard/* | logged in | kpis, status-chart, platform-chart, priority-chart, monthly-trend, sla-aging, developer-workload, recent-activities, pending-approvals |
| GET  /api/reports | logged in | Filtered rows: `platformId, status, priority, from, to` |
| GET  /api/reports/export | logged in | `?format=excel|pdf` file download |
| GET/POST/PUT/DELETE /api/admin/platforms, /users, /categories | Admin | Admin Masters CRUD |
| GET /api/platforms, /api/categories, /api/developers | logged in | Dropdown lookups |

## Workflow → status mapping

```
Raise Request → Pending Platform Approval
   Platform Owner Approve → Pending PGC Approval      | Reject → Rejected
      PGC Approve → In Development                    | Reject → Rejected
         Development 100% → Testing/UAT (auto, or set explicitly)
            → Production → Closed
```
Every transition writes a row to `ActivityLog`, which feeds the request
Timeline modal and the Dashboard's Recent Activities widget.
