renderShell("dashboard", "Dashboard");
document.getElementById("pageContent").appendChild(
  document.getElementById("dashboardTemplate").content.cloneNode(true)
);

const CHART_COLORS = [
    "#3B82F6",
    "#10B981",
    "#F59E0B",
    "#EF4444",
    "#8B5CF6",
    "#06B6D4",
    "#64748B"
];

function _clearCanvas(canvas) {
  const ctx = canvas.getContext("2d");
  const width = canvas.clientWidth * window.devicePixelRatio;
  const height = canvas.clientHeight * window.devicePixelRatio;
  canvas.width = width;
  canvas.height = height;
  ctx.setTransform(window.devicePixelRatio, 0, 0, window.devicePixelRatio, 0, 0);
  ctx.clearRect(0, 0, canvas.clientWidth, canvas.clientHeight);
  return ctx;
}

function _drawDoughnut(canvas, labels, values, colors) {
    const ctx = _clearCanvas(canvas);

    const width = canvas.clientWidth;
    const height = canvas.clientHeight;

    const centerX = width / 2 - 40; // Leave space for legend
    const centerY = height / 2;

    const radius = Math.min(width, height) * 0.38;
    const innerRadius = radius * 0.65;

    const total = values.reduce((a, b) => a + b, 0);

    if (!total) {
        ctx.fillStyle = "#E5E7EB";
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
        ctx.fill();

        ctx.fillStyle = "#6B7280";
        ctx.font = "14px Inter";
        ctx.textAlign = "center";
        ctx.fillText("No Data", centerX, centerY);

        return;
    }

    let start = -Math.PI / 2;

    values.forEach((value, i) => {

        const angle = (value / total) * Math.PI * 2;

        ctx.beginPath();
        ctx.moveTo(centerX, centerY);
        ctx.fillStyle = CHART_COLORS[i % CHART_COLORS.length];
        ctx.arc(centerX, centerY, radius, start, start + angle);
        ctx.closePath();
        ctx.fill();

        start += angle;
    });

    // Inner Circle
    ctx.beginPath();
    ctx.fillStyle = "#FFFFFF";
    ctx.arc(centerX, centerY, innerRadius, 0, Math.PI * 2);
    ctx.fill();

    // Total Count
    ctx.fillStyle = "#111827";
    ctx.font = "bold 26px Inter";
    ctx.textAlign = "center";
    ctx.fillText(total, centerX, centerY - 8);

    ctx.font = "13px Inter";
    ctx.fillStyle = "#6B7280";
    ctx.fillText("Requests", centerX, centerY + 18);

    // Legend
    let legendX = width - 145;
    let legendY = 45;

    ctx.textAlign = "left";

    labels.forEach((label, i) => {

        ctx.fillStyle = colors[i % colors.length];
        ctx.beginPath();
        ctx.arc(legendX, legendY + 5, 6, 0, Math.PI * 2);
        ctx.fill();

        ctx.fillStyle = "#374151";
        ctx.font = "13px Inter";
        ctx.fillText(
            `${label} (${values[i]})`,
            legendX + 15,
            legendY + 9
        );

        legendY += 28;
    });
}

function _drawBarChart(canvas, labels, values, options = {}) {
  const ctx = _clearCanvas(canvas);
  const width = canvas.clientWidth;
  const height = canvas.clientHeight;
  const margin = 30;
  const maxValue = Math.max(...values, 1);
  const barCount = values.length;
  const barSpacing = 16;
  const hasY = options.indexAxis === "y";
  const availableLength = hasY
    ? height - margin * 2 - (barCount - 1) * barSpacing
    : width - margin * 2 - (barCount - 1) * barSpacing;
  const barThickness = Math.max(18, availableLength / barCount);

  ctx.strokeStyle = "#E5E7EB";
  ctx.lineWidth = 1;
  ctx.beginPath();
  if (hasY) {
    const x0 = margin + 90;
    ctx.moveTo(x0, margin - 8);
    ctx.lineTo(x0, height - margin + 8);
  } else {
    const y0 = height - margin;
    ctx.moveTo(margin, y0);
    ctx.lineTo(width - margin, y0);
  }
  ctx.stroke();

  ctx.font = "12px Inter, sans-serif";
  ctx.fillStyle = "#374151";
  ctx.textBaseline = "middle";
  ctx.textAlign = hasY ? "left" : "center";

  values.forEach((value, index) => {
    ctx.fillStyle = CHART_COLORS[index % CHART_COLORS.length];
    if (hasY) {
      const y = margin + index * (barThickness + barSpacing);
      const barWidth = ((width - margin * 2 - 90) * value) / maxValue;
      ctx.fillRect(margin + 90, y, barWidth, barThickness);
      ctx.fillStyle = "#111827";
      ctx.fillText(labels[index], margin, y + barThickness / 2);
      ctx.textAlign = "right";
      ctx.fillText(value, margin + 90 + barWidth + 10, y + barThickness / 2);
      ctx.textAlign = "left";
    } else {
      const x = margin + index * (barThickness + barSpacing);
      const barHeight = ((height - margin * 2) * value) / maxValue;
      ctx.fillRect(x, height - margin - barHeight, barThickness, barHeight);
      ctx.fillStyle = "#111827";
      ctx.textAlign = "center";
      ctx.fillText(labels[index], x + barThickness / 2, height - margin + 16);
      ctx.fillText(value, x + barThickness / 2, height - margin - barHeight - 12);
    }
  });
}

function _drawLineChart(canvas, labels, values, options = {}) {
  const ctx = _clearCanvas(canvas);
  const width = canvas.clientWidth;
  const height = canvas.clientHeight;
  const margin = 32;
  const maxValue = Math.max(...values, 1);
  const pointCount = values.length;
  const effectiveWidth = width - margin * 2;
  const effectiveHeight = height - margin * 2;

  const points = values.map((value, index) => ({
    x: margin + (index / Math.max(pointCount - 1, 1)) * effectiveWidth,
    y: height - margin - (value / maxValue) * effectiveHeight,
    value,
    label: labels[index],
  }));

  ctx.strokeStyle = "#E5E7EB";
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(margin, height - margin);
  ctx.lineTo(width - margin, height - margin);
  ctx.stroke();

  ctx.strokeStyle = options.borderColor || "#2F6F9E";
  ctx.lineWidth = 2;
  ctx.beginPath();
  points.forEach((point, index) => {
    if (index === 0) ctx.moveTo(point.x, point.y);
    else ctx.lineTo(point.x, point.y);
  });
  ctx.stroke();

  if (options.fill) {
    ctx.fillStyle = options.backgroundColor || "rgba(47,111,158,0.12)";
    ctx.lineTo(points[points.length - 1].x, height - margin);
    ctx.lineTo(points[0].x, height - margin);
    ctx.closePath();
    ctx.fill();
  }

  ctx.fillStyle = "#111827";
  ctx.font = "12px Inter, sans-serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "top";
  points.forEach((point) => {
    ctx.beginPath();
    ctx.arc(point.x, point.y, 4, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillText(point.value, point.x, point.y - 20);
    ctx.fillText(point.label, point.x, height - margin + 6);
  });
}

const KPI_DEFS = [
  { key: "total", label: "Total Requests", cls: "" },
  { key: "open", label: "Open", cls: "kpi--accent" },
  { key: "inApproval", label: "In Approval", cls: "kpi--amber" },
  { key: "inDevelopment", label: "In Development", cls: "kpi--blue" },
  { key: "closed", label: "Closed", cls: "kpi--green" },
  { key: "rejected", label: "Rejected", cls: "kpi--red" },
];
async function loadKpis() {
  const kpis = await api("/dashboard/kpis") || {};

  document.getElementById("kpiRow").innerHTML = KPI_DEFS.map((d) => `
    <div class="kpi ${d.cls}">
      <div class="kpi__label">${d.label}</div>
      <div class="kpi__value">${kpis[d.key] ?? 0}</div>
    </div>
  `).join("");
}


async function loadStatusChart() {
  const rows = await api("/dashboard/status-chart") || [];

  const labels = rows.map((r) => r.status ?? "Unknown");
  const values = rows.map((r) => r.count ?? 0);

  _drawDoughnut(
    document.getElementById("statusChart"),
    labels,
    values,
    CHART_COLORS
  );
}


async function loadPlatformChart() {
  const rows = await api("/dashboard/platform-chart") || [];

  const labels = rows.map((r) => r.platform ?? "Unknown");
  const values = rows.map((r) => r.count ?? 0);

  _drawBarChart(
    document.getElementById("platformChart"),
    labels,
    values,
    { indexAxis: "x" }
  );
}


async function loadPriorityChart() {
  const rows = await api("/dashboard/priority-chart") || [];

  const labels = rows.map((r) => r.priority ?? "Unknown");
  const values = rows.map((r) => r.count ?? 0);

  _drawBarChart(
    document.getElementById("priorityChart"),
    labels,
    values,
    { indexAxis: "y" }
  );
}


async function loadTrendChart() {
  const rows = await api("/dashboard/monthly-trend") || [];

  const labels = rows.map((r) => r.month ?? "");
  const values = rows.map((r) => r.count ?? 0);

  _drawLineChart(
    document.getElementById("trendChart"),
    labels,
    values,
    {
      borderColor: "#2F6F9E",
      backgroundColor: "rgba(47,111,158,0.12)",
      fill: true
    }
  );
}


async function loadSlaChart() {
  const buckets = await api("/dashboard/sla-aging") || {};

  const labels = Object.keys(buckets);
  const values = Object.values(buckets);

  _drawBarChart(
    document.getElementById("slaChart"),
    labels,
    values,
    { indexAxis: "x" }
  );
}


async function loadWorkloadChart() {
  const rows = await api("/dashboard/developer-workload") || [];

  const labels = rows.map((r) => r.developer ?? "Unassigned");
  const values = rows.map((r) => r.activeItems ?? 0);

  _drawBarChart(
    document.getElementById("workloadChart"),
    labels,
    values,
    { indexAxis: "y" }
  );
}


async function loadRecentActivities() {
  const rows = await api("/dashboard/recent-activities") || [];

  document.getElementById("recentActivities").innerHTML =
    rows.length
      ? rows.map((a) => `
          <li>
            <time>${fmtDateTime(a.timestamp)}</time>
            <span>${a.action ?? ""} — ${a.userName ?? "System"}</span>
          </li>
        `).join("")
      : `<li>No activity yet.</li>`;
}


async function loadPendingApprovals() {

  const user = Auth.getUser();

  if (!user || !["Platform Owner", "PGC", "Admin"].includes(user.role)) {
    document.getElementById("pendingApprovalsCard").style.display = "none";
    return;
  }

  const rows = await api("/dashboard/pending-approvals") || [];

  const container = document.getElementById("pendingApprovals");

  if (!rows.length) {
    container.innerHTML = `
      <div class="empty-state">
        <h3>All caught up</h3>
        No pending approvals right now.
      </div>`;
    return;
  }


  container.innerHTML = `
  <table>
    <thead>
      <tr>
        <th>Request</th>
        <th>Platform</th>
        <th>Priority</th>
        <th>Raised Date</th>
        <th>View</th>
      </tr>
    </thead>

    <tbody>

    ${rows.map((r) => `
      <tr>

        <td class="req-id">
          ${reqCode(r.requestId)}
        </td>

        <td>
          ${r.platformName ?? "-"}
        </td>

        <td>
          <span class="priority priority--${r.priority ?? ""}">
            ${r.priority ?? "-"}
          </span>
        </td>

        <td>
          <span class="target-date">
            ${r.createdDate ? fmtDate(r.createdDate) : "-"}
          </span>
        </td>

        <td>
          <button 
            class="btn btn-secondary btn-sm"
            onclick="openRequestModal(${r.requestId})">
            View
          </button>
        </td>

      </tr>
    `).join("")}

    </tbody>
  </table>`;
}



Promise.all([
  loadKpis(),
  loadStatusChart(),
  loadPlatformChart(),
  loadPriorityChart(),
  loadTrendChart(),
  loadSlaChart(),
  loadWorkloadChart(),
  loadRecentActivities(),
  loadPendingApprovals()
])
.catch((e) => {
  console.error("Dashboard loading error:", e);
  showToast(e.message || "Dashboard loading failed", "error");
});