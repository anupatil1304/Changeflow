renderShell("dev", "Development Tracking");
document.getElementById("pageContent").appendChild(
  document.getElementById("pageTemplate").content.cloneNode(true)
);

const user = Auth.getUser();
const canEdit = ["Developer", "Admin"].includes(user.role);

function renderTable(rows) {
  const wrap = document.getElementById("tableWrap");
  if (!rows.length) {
    wrap.innerHTML = `<div class="empty-state"><h3>Nothing in development</h3>Approved requests will appear here once PGC signs off.</div>`;
    return;
  }
  wrap.innerHTML = `
    <table>
      <thead><tr><th>Request</th><th>Platform</th><th>Owner</th><th>Target</th><th>Progress</th><th>Status</th><th></th></tr></thead>
      <tbody>
        ${rows.map((d) => `
          <tr>
            <td class="req-id">${reqCode(d.requestId)}</td>
            <td>${d.platformName || "—"}</td>
            <td>${d.assigneeName || "Unassigned"}</td>
            <td>
    ${fmtDate(d.targetDate)}

    ${d.dueStatus === "Due Soon"
      ? `<div class="helper-text" style="color:#f59e0b;font-weight:600;">⚠ Due Soon</div>`
      : d.dueStatus === "Overdue"
        ? `<div class="helper-text" style="color:#dc2626;font-weight:600;">🔴 Overdue</div>`
        : d.dueStatus === "Completed"
          ? `<div class="helper-text" style="color:#16a34a;font-weight:600;">✔ Completed</div>`
          : ""
    }
</td>
            <td style="min-width:120px;">
              <div class="progress-bar"><div class="progress-bar__fill" style="width:${d.progress}%"></div></div>
              <div class="helper-text">${d.progress}%</div>
            </td>
            <td><span class="status ${statusClass(d.status)}">${d.status || "—"}</span></td>
<td style="display:flex; gap:8px; justify-content:center;">
  <button
      class="btn btn-outline-primary btn-sm"
      onclick="openRequestModal(${d.requestId})">
      View
  </button>

  ${canEdit ? `
    <button
        class="btn btn-primary btn-sm"
        onclick="openDevModal(${d.requestId}, '${d.assignedTo || ""}', '${d.startDate || ""}', '${d.targetDate || ""}', ${d.progress})">
        Update
    </button>
  ` : ""}
</td>
          </tr>`).join("")}
      </tbody>
    </table>`;
}

async function loadDevelopment() {
  try {
    const rows = await api("/development");
    renderTable(rows);
  } catch (e) {
    showToast(e.message, "error");
  }
}

let devDropdownCache = null;
async function getDevDropdown() {
  if (!devDropdownCache) devDropdownCache = await api("/developers");
  return devDropdownCache;
}

window.openDevModal = async (requestId, assignedTo, startDate, targetDate, progress) => {
  const node = document.getElementById("devModalTemplate").content.cloneNode(true);
  document.body.appendChild(node);
  const backdrop = document.body.lastElementChild;
  backdrop.querySelector("#dmReqSummary").textContent = reqCode(requestId);

  const devs = await getDevDropdown();
  backdrop.querySelector("#dmAssignee").innerHTML = devs
    .map((d) => `<option value="${d.userId}" ${String(d.userId) === String(assignedTo) ? "selected" : ""}>${d.name}</option>`).join("");
  backdrop.querySelector("#dmStart").value = startDate || "";
  backdrop.querySelector("#dmTarget").value = targetDate || "";

  const targetInput = backdrop.querySelector("#dmTarget");

  if (targetDate) {
    targetInput.readOnly = true;
    targetInput.style.background = "#f3f4f6";
    targetInput.style.cursor = "not-allowed";
  }

  const close = () => backdrop.remove();
  backdrop.querySelector(".modal__close").addEventListener("click", close);
  backdrop.addEventListener("click", (e) => { if (e.target === backdrop) close(); });

  backdrop.querySelector("#dmSave").addEventListener("click", async () => {
    try {
      await api(`/development/${requestId}`, {
        method: "PUT",
        json: {
          assignedTo: Number(backdrop.querySelector("#dmAssignee").value),
          startDate: backdrop.querySelector("#dmStart").value || null,
          targetDate: backdrop.querySelector("#dmTarget").value || null,
          status: backdrop.querySelector("#dmStatus").value || undefined,
        },
      });
      showToast(`${reqCode(requestId)} updated.`, "success");
      close();
      loadDevelopment();
    } catch (e) {
      showToast(e.message, "error");
    }
  });
};

loadDevelopment();
