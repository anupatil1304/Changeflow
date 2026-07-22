# ChangeFlow — Frontend (Plain HTML / CSS / JS)

Static, no-build-step frontend for the 9 screens in the Application Design
Pack. Talks to the Flask backend purely over `fetch()` + JWT — no framework,
no bundler.

## Running it

The backend must be running first (see `../backend/README.md`), then serve
this folder with any static file server, e.g.:

```bash
cd frontend
python3 -m http.server 8080
```

Open http://127.0.0.1:8080 and log in with one of the demo accounts printed
by `backend/utils/seed.py`.

If the API isn't on `http://127.0.0.1:5000`, edit `API_BASE` at the top of
`js/api.js`.

## Pages ↔ Design Pack screens

| File | Screen |
|---|---|
| index.html | Login |
| dashboard.html | Dashboard |
| raise-request.html | Raise Request |
| my-requests.html | My Requests |
| platform-approval.html | Platform Owner Approval |
| pgc-review.html | PGC Review |
| development.html | Development Tracking |
| reports.html | Reports |
| admin.html | Admin Masters |

## Shared modules (js/)

- `api.js` — fetch wrapper, JWT storage (localStorage), toast helper, date/status formatters
- `shell.js` — renders the sidebar + topbar, filters nav links by the logged-in user's role
- `request-modal.js` — the "workflow rail" + approval/activity timeline modal, reused by My Requests, Platform Owner Approval, PGC Review, Development Tracking
- `approval-shared.js` — shared table + decide-modal logic for the two approval-queue screens

## Design system

Tokens live at the top of `css/style.css`: ink-navy sidebar, teal primary
accent, clay/amber/green/red/blue status colors, Space Grotesk for headings,
Inter for UI text, IBM Plex Mono for request IDs and timestamps. The one
signature element is the **workflow rail** — a horizontal stepper
(Raised → Platform Owner → PGC → Development → Testing/UAT → Production)
shown in the request detail modal, echoing the Workflow Diagram in the
Design Pack.

## Role-based navigation

`js/shell.js`'s `NAV_ITEMS` array controls which sidebar links each role
sees, matching the Role & Permission Matrix:

- **Requester** — Dashboard, Raise Request, My Requests, Reports
- **Platform Owner** — Dashboard, My Requests, Platform Owner Approval, Reports
- **PGC** — Dashboard, My Requests, PGC Review, Development Tracking (view), Reports
- **Developer** — Dashboard, My Requests, Development Tracking, Reports
- **Admin** — everything, including Admin Masters
