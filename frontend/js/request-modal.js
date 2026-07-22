/* ============================================================================
   Shared "request detail" modal — workflow rail + approvals + activity timeline.
   Usage: openRequestModal(requestId)
   Requires css/style.css (.modal, .rail, .timeline classes) to be loaded.
   ============================================================================ */

const RAIL_STEPS = ["Raised", "Platform Owner", "PGC", "BRD Submission", "Development", "QA", "UAT", "Production"];

function railIndexForStatus(status) {
  switch (status) {
    case "Pending Platform Approval":
      return 1;

    case "Pending PGC Approval":
      return 2;

    case "BRD Submission":
      return 3;

    case "In Development":
      return 4;

    case "QA":
      return 5;

    case "Testing/UAT":
      return 6;

    case "Production":
    case "Closed":
      return 7;

    default:
      return 0;
  }
}

function buildRail(reqData) {
  const rejected = reqData.status === "Rejected";
  const rejectedApproval = (reqData.approvals || []).find((a) => a.decision === "Rejected");
  const currentIdx = rejected
    ? RAIL_STEPS.indexOf(rejectedApproval && rejectedApproval.level === "PGC" ? "PGC" : "Platform Owner")
    : railIndexForStatus(reqData.status);

  return `
    <div class="rail">
      ${RAIL_STEPS.map((label, i) => {
        let cls = "rail__step";
        if (rejected && i === currentIdx) cls += " rail__step--rejected";
        else if (i < currentIdx || (i === currentIdx && ["Production", "Closed"].includes(reqData.status))) cls += " rail__step--done";
        else if (i === currentIdx) cls += " rail__step--current";
        const lineDone = i <= currentIdx && !(rejected && i === currentIdx);
        return `
          <div class="${cls}">
            <div class="rail__line ${lineDone ? "rail__line--done" : ""}"></div>
            <div class="rail__node">${rejected && i === currentIdx ? "✕" : (i < currentIdx ? "✓" : i + 1)}</div>
            <div class="rail__label">${label}</div>
          </div>`;
      }).join("")}
    </div>`;
}

async function openRequestModal(requestId) {
  let data;
  try {
    data = await api(`/requests/${requestId}`);
  } catch (e) {
    showToast(e.message, "error");
    return;
  }

  const approvalsHtml = (data.approvals || []).map((a) => `
    <li>
      <time>${fmtDateTime(a.date)}</time>
      <span><b>${a.level}</b> — ${a.decision} by ${a.approverName || "—"}${a.remarks ? ` · "${a.remarks}"` : ""}</span>
    </li>`).join("") || "<li>No approvals recorded yet.</li>";

  const timelineHtml = (data.timeline || []).map((t) => `
    <li><time>${fmtDateTime(t.timestamp)}</time><span>${t.action} — ${t.userName}</span></li>`).join("")
    || "<li>No activity yet.</li>";

  const devHtml = data.development ? `
    <div class="field-row" style="margin-top:14px;">
      <div><label>Assigned Developer</label>${data.development.assigneeName || "Unassigned"}</div>
      <div><label>Progress</label>
        <div class="progress-bar"><div class="progress-bar__fill" style="width:${data.development.progress}%"></div></div>
        <div class="helper-text">
  ${data.development.progress}% complete
  ${
    data.development.dueStatus === "Due Soon"
      ? " · 🟠 Due Soon"
      : data.development.dueStatus === "Overdue"
      ? " · 🔴 Overdue"
      : data.development.dueStatus === "Completed"
      ? " · 🟢 Completed"
      : ""
  }
  · Target ${fmtDate(data.development.targetDate)}
</div>
    </div>` : "";

  const backdrop = document.createElement("div");
  backdrop.className = "modal-backdrop";
  backdrop.innerHTML = `
    <div class="modal">
      <div class="modal__head">
        <h3>${reqCode(data.requestId)} <span class="status ${statusClass(data.status)}" style="margin-left:8px;">${data.status}</span></h3>
        <button class="modal__close" aria-label="Close">&times;</button>
      </div>
      <div class="modal__body">
        ${buildRail(data)}
        <div class="field-row" style="margin-top:18px;">
          <div><label>Platform</label>${data.platformName}</div>
          <div><label>Priority</label><span class="priority priority--${data.priority}">${data.priority}</span></div>
        </div>
        <div class="field" style="margin-top:4px;">
  <label>Description</label>
  <div>${data.description}</div>
</div>

<div class="field" style="margin-top:12px;">
  <label>Attachment</label>
${
  data.attachmentPath
    ? `<a
          href="http://127.0.0.1:5000/uploads/${data.attachmentPath}"
          target="_blank"
          class="btn btn-primary btn-sm"
          style="text-decoration:none;">
          View
       </a>`
    : `<span style="color:#6c757d;">No attachment uploaded</span>`
}
</div>
        <div class="field-row">
          <div><label>Requested By</label>${data.requesterName}</div>
          <div><label>Raised On</label>${fmtDate(data.createdDate)}</div>
        </div>
        ${devHtml}
        <div class="section-title" style="margin-top:20px;">Approval Trail</div>
        <ul class="timeline">${approvalsHtml}</ul>
        <div class="section-title" style="margin-top:20px;">Activity Timeline</div>
        <ul class="timeline">${timelineHtml}</ul>
      </div>
    </div>`;

  document.body.appendChild(backdrop);
  const close = () => backdrop.remove();
  backdrop.querySelector(".modal__close").addEventListener("click", close);
  backdrop.addEventListener("click", (e) => { if (e.target === backdrop) close(); });
}
