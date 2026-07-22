renderShell("myrequests", "My Requests");

document.getElementById("pageContent").appendChild(
  document.getElementById("pageTemplate").content.cloneNode(true)

);

const searchInput = document.getElementById("search");
const statusFilter = document.getElementById("statusFilter");
let debounceTimer;
const currentUser = Auth.getUser();

function renderTable(rows) {
  const wrap = document.getElementById("tableWrap");

  if (!rows.length) {
    wrap.innerHTML = `
      <div class="empty-state">
        <h3>No requests found</h3>
        <p>Try adjusting your search or status filter.</p>
      </div>`;
    return;
  }

  wrap.innerHTML = `
    <table class="table">
      <thead>
        <tr>
          <th>Request</th>
          <th>Type</th>
          <th>Platform</th>
          <th>Priority</th>
          <th>Status</th>
          <th>Raised</th>
          <th style="text-align:center;">View</th>
        </tr>
      </thead>

      <tbody>
        ${rows.map(r => `
          <tr>
            <td class="req-id">${reqCode(r.requestId)}</td>

            <td>${r.type}</td>

            <td>${r.platformName}</td>

            <td>
              <span class="priority priority--${r.priority}">
                ${r.priority}
              </span>
            </td>

            <td>
              <span class="status ${statusClass(r.status)}">
                ${r.status}
              </span>
            </td>

            <td>${fmtDate(r.createdDate)}</td>

            <td style="text-align:center;">
              <div style="display:inline-flex; gap:0.5rem; flex-wrap:wrap; justify-content:center; align-items:center;">
                <button
                  class="btn btn-primary btn-sm"
                  onclick="openRequestModal(${r.requestId})"
                  title="View Request">
                  View
                </button>
                ${r.requesterId === currentUser?.userId ? `
                <button
                  class="btn btn-danger btn-sm"
                  ${r.status === "Pending Platform Approval" ? "" : "disabled"}
                  title="${r.status === "Pending Platform Approval" ? "Delete this request" : "This request can no longer be deleted because the Platform Owner has already taken action."}"
                  onclick="deleteRequest(${r.requestId})">
                  Delete
                </button>` : ""}
              </div>
            </td>

          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}

async function loadRequests() {
  try {
    const rows = await api("/requests", {
      params: {
        search: searchInput.value,
        status: statusFilter.value
      }
    });

    renderTable(rows);

  } catch (e) {
    showToast(e.message, "error");
  }
}

async function deleteRequest(requestId) {
  if (!confirm("Are you sure you want to delete this request? This action cannot be undone.")) {
    return;
  }

  try {
    await api(`/requests/${requestId}`, { method: "DELETE" });
    showToast("Request deleted.", "success");
    loadRequests();
  } catch (e) {
    showToast(e.message, "error");
  }
}

searchInput.addEventListener("input", () => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(loadRequests, 300);
});

statusFilter.addEventListener("change", loadRequests);

document.getElementById("clearBtn").addEventListener("click", () => {
  searchInput.value = "";
  statusFilter.value = "";
  loadRequests();
});

loadRequests();