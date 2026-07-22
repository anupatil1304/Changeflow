renderShell("reports", "Reports");
document.getElementById("pageContent").appendChild(
  document.getElementById("pageTemplate").content.cloneNode(true)
);

async function loadPlatformFilter() {
  const platforms = await api("/platforms");
  document.getElementById("fPlatform").insertAdjacentHTML(
    "beforeend",
    platforms.map((p) => `<option value="${p.platformId}">${p.platformName}</option>`).join("")
  );
}

function currentFilters() {
  return {
    platformId: document.getElementById("fPlatform").value,
    status: document.getElementById("fStatus").value,
    priority: document.getElementById("fPriority").value,
    from: document.getElementById("fFrom").value,
    to: document.getElementById("fTo").value,
  };
}

function renderTable(rows) {
  const wrap = document.getElementById("tableWrap");
  if (!rows.length) {
    wrap.innerHTML = `<div class="empty-state"><h3>No matching requests</h3>Adjust the filters above and try again.</div>`;
    return;
  }
  wrap.innerHTML = `
    <table>
      <thead><tr><th>Request</th><th>Type</th><th>Platform</th><th>Requester</th><th>Priority</th><th>Status</th><th>Raised</th></tr></thead>
      <tbody>
        ${rows.map((r) => `
          <tr>
            <td class="req-id">${reqCode(r.requestId)}</td>
            <td>${r.type}</td>
            <td>${r.platformName}</td>
            <td>${r.requesterName}</td>
            <td><span class="priority priority--${r.priority}">${r.priority}</span></td>
            <td><span class="status ${statusClass(r.status)}">${r.status}</span></td>
            <td>${fmtDate(r.createdDate)}</td>
          </tr>`).join("")}
      </tbody>
    </table>`;
}

async function loadReport() {
  try {
    const rows = await api("/reports", { params: currentFilters() });
    renderTable(rows);
  } catch (e) {
    showToast(e.message, "error");
  }
}

async function exportReport(format) {
  try {
    const res = await api("/reports/export", { params: { ...currentFilters(), format }, raw: true });
    if (!res.ok) throw new Error("Export failed");
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = format === "pdf" ? "requests_report.pdf" : "requests_report.xlsx";
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  } catch (e) {
    showToast(e.message, "error");
  }
}

document.getElementById("applyBtn").addEventListener("click", loadReport);
document.getElementById("exportExcelBtn").addEventListener("click", () => exportReport("excel"));
document.getElementById("exportPdfBtn").addEventListener("click", () => exportReport("pdf"));

loadPlatformFilter().catch((e) => showToast(e.message, "error"));
loadReport();
