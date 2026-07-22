/* ============================================================================
   App shell: sidebar + topbar, rendered into <div id="shell"></div>
   Call renderShell('dashboard') at the top of each page's script,
   passing the key of the current nav item to highlight.
   ============================================================================ */

const NAV_ITEMS = [
  { key: "admin",      label: "Admin Masters",          href: "admin.html",               roles: ["Admin"] },
  { key: "dashboard",  label: "Dashboard",              href: "dashboard.html",           roles: ["Requester", "Platform Owner", "PGC", "Developer", "Admin"] },
  { key: "raise",      label: "Raise Request",          href: "raise-request.html",       roles: ["Requester", "Admin"] },
  { key: "myrequests", label: "My Requests",            href: "my-requests.html",         roles: ["Requester", "Admin"] },
  { key: "platform",   label: "Platform Owner Approval",href: "platform-approval.html",   roles: ["Platform Owner", "Admin"] },
  { key: "pgc",        label: "PGC Review",             href: "pgc-review.html",          roles: ["PGC", "Admin"] },
  { key: "dev",        label: "Development Tracking",   href: "development.html",         roles: ["Developer", "Admin", "Platform Owner"] },
  { key: "reports",    label: "Reports",                href: "reports.html",             roles: ["Requester", "Platform Owner", "PGC", "Developer", "Admin"] },
];

function renderShell(activeKey, pageTitle) {
  Auth.requireLogin();
  const user = Auth.getUser();
  if (!user) return;

  const links = NAV_ITEMS
    .filter((item) => item.roles.includes(user.role))
    .map((item) => `
      <a class="sidebar__link ${item.key === activeKey ? "active" : ""}" href="${item.href}">
        <span class="dot"></span>${item.label}
      </a>`)
    .join("");

  const shellHtml = `
    <div class="app-shell">
      <aside class="sidebar">
        <div class="sidebar__brand">Change<span>Flow</span></div>
        <nav class="sidebar__nav">${links}</nav>
        <div class="sidebar__foot">
          <b>${user.name}</b>
          ${user.platformName ? user.platformName : "All platforms"}
        </div>
      </aside>
      <div class="main">
        <header class="topbar">
          <h1>${pageTitle || ""}</h1>
          <div class="topbar__right">
            <span class="badge-role">${user.role}</span>
            <button class="btn-logout" id="logoutBtn">Log out</button>
          </div>
        </header>
        <main class="content" id="pageContent"></main>
      </div>
    </div>
  `;

  document.getElementById("shell").innerHTML = shellHtml;
  document.getElementById("logoutBtn").addEventListener("click", () => Auth.logout());
}
