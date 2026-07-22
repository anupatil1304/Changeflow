
renderShell("raise", "Raise Request");
document.getElementById("pageContent").appendChild(
  document.getElementById("pageTemplate").content.cloneNode(true)
);

async function loadLookups() {
  const [platforms, categories] = await Promise.all([api("/platforms"), api("/categories")]);
  document.getElementById("platformId").innerHTML =
    platforms.map((p) => `<option value="${p.platformId}">${p.platformName}</option>`).join("");
  document.getElementById("categoryId").innerHTML =
    `<option value="">— Select category —</option>` +
    categories.map((c) => `<option value="${c.categoryId}">${c.categoryName}</option>`).join("");
}

document.getElementById("raiseForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const submitBtn = document.getElementById("submitBtn");
  submitBtn.disabled = true;
  submitBtn.textContent = "Submitting…";

  const form = new FormData();
  form.append("type", document.getElementById("type").value);
  form.append("platformId", document.getElementById("platformId").value);
  form.append("priority", document.getElementById("priority").value);
  form.append("description", document.getElementById("description").value);
  const categoryId = document.getElementById("categoryId").value;

  if (categoryId) form.append("categoryId", categoryId);
const file = document.getElementById("attachment").files[0];

if (file) {
  // 2 MB limit
  if (file.size > 2 * 1024 * 1024) {
    showToast("File size must not exceed 2 MB", "error");
    submitBtn.disabled = false;
    submitBtn.textContent = "Submit Request";
    return;
  }

  form.append("attachment", file);
}

  try {
    const created = await api("/requests", { method: "POST", form });
    showToast(`${reqCode(created.requestId)} submitted successfully`, "success");
    document.getElementById("raiseForm").reset();
    setTimeout(() => { window.location.href = "my-requests.html"; }, 900);
  } catch (err) {
    showToast(err.message, "error");
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = "Submit Request";
  }
});

loadLookups().catch((e) => showToast(e.message, "error"));
