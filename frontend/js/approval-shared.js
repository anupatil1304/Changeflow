/* ============================================================================
   Shared behaviour for the two "approval queue" screens:
   Platform Owner Approval and PGC Review both show a queue of pending
   requests with Approve/Reject + Remarks — only the endpoints differ.
   ============================================================================ */

function initApprovalScreen({ title, pendingEndpoint, decideEndpoint }) {
  renderShell(title, title === "platform" ? "Platform Owner Approval" : "PGC Review");
  document.getElementById("pageContent").appendChild(
    document.getElementById("pageTemplate").content.cloneNode(true)
  );

  function renderTable(rows) {
    const wrap = document.getElementById("tableWrap");
    if (!rows.length) {
      wrap.innerHTML = `<div class="empty-state"><h3>Queue is empty</h3>No requests are waiting on your decision.</div>`;
      return;
    }
    wrap.innerHTML = `
      <table>
        <thead><tr><th>Request</th><th>Platform</th><th>Priority</th><th>Requested By</th><th>Raised</th><th></th></tr></thead>
        <tbody>
          ${rows.map((r) => `
            <tr>
              <td class="req-id">${reqCode(r.requestId)}</td>
              <td>${r.platformName}</td>
              <td><span class="priority priority--${r.priority}">${r.priority}</span></td>
              <td>${r.requesterName}</td>
              <td>${fmtDate(r.createdDate)}</td>
 <td style="text-align:center;">
  <div style="display:flex; justify-content:center; gap:8px;">
  <button
      class="btn btn-outline-primary btn-sm"
      onclick="openRequestModal(${r.requestId})">
      View
  </button>

  <button
      class="btn btn-primary btn-sm"
      onclick="openDecisionModal(${r.requestId}, '${(r.description || "").replace(/'/g, "").slice(0, 60)}')">
      Decide
  </button>
</td>
            </tr>`).join("")}
        </tbody>
      </table>`;
  }

  async function loadQueue() {
    try {
      const rows = await api(pendingEndpoint);
      renderTable(rows);
    } catch (e) {
      showToast(e.message, "error");
    }
  }

  window.openDecisionModal = (requestId, summary) => {
    const node = document.getElementById("decisionModalTemplate").content.cloneNode(true);
    document.body.appendChild(node);
    const backdrop = document.body.lastElementChild;
    backdrop.querySelector("#dmReqSummary").textContent = `${reqCode(requestId)} — ${summary}…`;

    const close = () => backdrop.remove();
    backdrop.querySelector(".modal__close").addEventListener("click", close);
    backdrop.addEventListener("click", (e) => { if (e.target === backdrop) close(); });

    const submit = async (decision) => {
      const remarks = backdrop.querySelector("#dmRemarks").value.trim();
      if (decision === "Rejected" && !remarks) {
        showToast("Please add remarks before rejecting the request.", "error");
        return;
      }
      try {
        await api(decideEndpoint(requestId), {
          method: "POST",
          json: { decision, remarks },
        });
        showToast(`${reqCode(requestId)} ${decision.toLowerCase()}.`, "success");
        close();
        loadQueue();
      } catch (e) {
        showToast(e.message, "error");
      }
    };
    backdrop.querySelector("#dmApprove").addEventListener("click", () => submit("Approved"));
    backdrop.querySelector("#dmReject").addEventListener("click", () => submit("Rejected"));
  };

  loadQueue();
}
