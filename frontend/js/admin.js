renderShell("admin", "Admin Masters");

let editingPlatformId = null;
let editingUserId = null;

document.getElementById("pageContent").appendChild(
  document.getElementById("pageTemplate").content.cloneNode(true)
);

// ---- Tabs ----
document.querySelectorAll(".tab-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    document.querySelectorAll(".tab-panel").forEach((p) => (p.style.display = "none"));
    document.getElementById(`tab-${btn.dataset.tab}`).style.display = "block";
  });
});

// ---- Platforms ----
async function loadPlatforms() {

  const [platforms, users, businesses] = await Promise.all([
    api("/admin/platforms"),
    api("/admin/users"),
    api("/admin/business")
  ]);

  document.getElementById("platformsTableCard").innerHTML = `
    <div class="section-title">Platforms</div>
    <table>
      <thead>
<tr>
<th>ID</th>
<th>Name</th>
<th>Status</th>
<th></th>
</tr>
</thead>
      <tbody>
        ${platforms.map((p) => `
          <tr>
            <td class="mono">${p.platformId}</td>
            <td>${p.platformName}</td>
            <td><span class="status ${p.isActive ? "status--approved" : "status--closed"}">${p.isActive ? "Active" : "Inactive"}</span></td>
            <td>
    <button class="btn btn-primary btn-sm"
        onclick="editPlatform(${p.platformId})">
        Edit
    </button>

    <button class="btn btn-secondary btn-sm"
        onclick="togglePlatformStatus(${p.platformId}, ${p.isActive})">
        ${p.isActive ? "Deactivate" : "Activate"}
    </button>
</td>
          </tr>`).join("")}
      </tbody>
    </table>`;
}

document.getElementById("pfSubmit").addEventListener("click", async () => {
    try {

        const data = {
            platformName: document.getElementById("pfName").value
        };

        if (editingPlatformId) {

            await api(`/admin/platforms/${editingPlatformId}`, {
                method: "PUT",
                json: data
            });

            showToast("Platform updated.", "success");

            editingPlatformId = null;

            document.getElementById("pfSubmit").textContent = "Add Platform";

        } else {

            await api("/admin/platforms", {
                method: "POST",
                json: data
            });

            showToast("Platform added.", "success");
        }

        document.getElementById("pfName").value = "";

        loadPlatforms();

    } catch (e) {
        showToast(e.message, "error");
    }
});

window.togglePlatformStatus = async (id, isActive) => {
    try {

        await api(`/admin/platforms/${id}/status`, {
            method: "PUT",
            json: {
                isActive: !isActive
            }
        });

        showToast(
            isActive ? "Platform deactivated." : "Platform activated.",
            "success"
        );

        loadPlatforms();

    } catch (e) {
        showToast(e.message, "error");
    }
};

// ---- Users ----
async function loadUsers() {
  const [users, roles, platforms,businesses] = await Promise.all([api("/admin/users"), api("/admin/roles"), api("/admin/platforms"), api("/admin/business")]);

  console.log("USERS FROM API:", users);

  document.getElementById("usRole").innerHTML = roles.map((r) => `<option value="${r.roleId}">${r.roleName}</option>`).join("");
  document.getElementById("usPlatform").innerHTML =
    `<option value="">— None —</option>` + platforms.map((p) => `<option value="${p.platformId}">${p.platformName}</option>`).join("");

  document.getElementById("usBusiness").innerHTML =
    `<option value="">— None —</option>` +businesses.map((b) => `<option value="${b.businessId}">${b.businessName}</option>`).join("");

  document.getElementById("usersTableCard").innerHTML = `
    <div class="section-title">Users</div>
    <table>
      <thead><tr><th>Name</th><th>Email</th><th>Role</th><th>Platform</th><th>Business</th><th>Status</th><th></th></tr></thead>
      <tbody>
        ${users.map((u) => `
          <tr>
            <td>${u.name}</td>
            <td class="mono">${u.email}</td>
            <td>${u.role}</td>
            <td>${u.platformName || "—"}</td>
            <td>${u.businessName || "—"}</td>
            <td><span class="status ${u.status === "Active" ? "status--approved" : "status--closed"}">${u.status}</span></td>
            <td>
    <button class="btn btn-primary btn-sm"
        onclick="editUser(${u.userId})">
        Edit
    </button>

    <button class="btn btn-secondary btn-sm"
        onclick="toggleUserStatus(${u.userId}, '${u.status}')">
        ${u.status === "Active" ? "Deactivate" : "Activate"}
    </button>
</td>
          </tr>`).join("")}
      </tbody>
    </table>`;
}

document.getElementById("usSubmit").addEventListener("click", async () => {
    try {

        const data = {
            name: document.getElementById("usName").value,
            email: document.getElementById("usEmail").value,
            password: document.getElementById("usPassword").value,
            roleId: Number(document.getElementById("usRole").value),
            platformId: document.getElementById("usPlatform").value || null,
            businessId: document.getElementById("usBusiness").value || null,
        };

        if (editingUserId) {

            await api(`/admin/users/${editingUserId}`, {
                method: "PUT",
                json: data
            });

            showToast("User updated.", "success");

            editingUserId = null;

            document.getElementById("usSubmit").textContent = "Add User";

        } else {

            await api("/admin/users", {
                method: "POST",
                json: data
            });

            showToast("User added.", "success");
        }

        document.getElementById("usName").value = "";
        document.getElementById("usEmail").value = "";
        document.getElementById("usPassword").value = "Passw0rd!";
        document.getElementById("usPlatform").value = "";
        document.getElementById("usBusiness").value = "";

        loadUsers();

    } catch (e) {
        showToast(e.message, "error");
    }
});

window.toggleUserStatus = async (id, status) => {

    try {

        await api(`/admin/users/${id}`, {
            method: "PUT",
            json: {
                status: status === "Active" ? "Inactive" : "Active"
            }
        });

        showToast(
            status === "Active"
                ? "User deactivated."
                : "User activated.",
            "success"
        );

        loadUsers();

    } catch (e) {
        showToast(e.message, "error");
    }
};

// ---- Categories ----
async function loadCategories() {
  const categories = await api("/admin/categories");
  document.getElementById("categoriesTableCard").innerHTML = `
    <div class="section-title">Categories</div>
    <table>
      <thead><tr><th>ID</th><th>Name</th><th>Type</th><th>Status</th><th></th></tr></thead>
      <tbody>
        ${categories.map((c) => `
          <tr>
            <td class="mono">${c.categoryId}</td>
            <td>${c.categoryName}</td>
            <td>${c.type}</td>
            <td><span class="status ${c.isActive ? "status--approved" : "status--closed"}">${c.isActive ? "Active" : "Inactive"}</span></td>
            <td>   

    <button class="btn btn-secondary btn-sm"
        onclick="toggleCategoryStatus(${c.categoryId}, ${c.isActive})">
        ${c.isActive ? "Deactivate" : "Activate"}
    </button>
</td>
          </tr>`).join("")}
      </tbody>
    </table>`;
}

document.getElementById("catSubmit").addEventListener("click", async () => {
  try {
    await api("/admin/categories", {
      method: "POST",
      json: { categoryName: document.getElementById("catName").value, type: document.getElementById("catType").value },
    });
    document.getElementById("catName").value = "";
    showToast("Category added.", "success");
    loadCategories();
  } 
  catch (e) { showToast(e.message, "error"); }
});

window.toggleCategoryStatus = async (id, isActive) => {
  try {
    await api(`/admin/categories/${id}/status`, { method: "PUT", json: { isActive: !isActive } });
    showToast(isActive ? "Category deactivated." : "Category activated.", "success");
    loadCategories();
  } catch (e) { showToast(e.message, "error"); }
};

loadPlatforms().catch((e) => showToast(e.message, "error"));
loadUsers().catch((e) => showToast(e.message, "error"));
loadCategories().catch((e) => showToast(e.message, "error"));


window.editPlatform = async function (id) {

    const platforms = await api("/admin/platforms");

    const platform = platforms.find(p => p.platformId === id);

    if (!platform) return;

    editingPlatformId = id;

    document.getElementById("pfName").value = platform.platformName;

    document.getElementById("pfSubmit").textContent = "Update Platform";
};

window.editUser = async function (id) {

    const users = await api("/admin/users");

    const user = users.find(u => u.userId === id);

    if (!user) return;

    editingUserId = id;

    document.getElementById("usName").value = user.name;
    document.getElementById("usEmail").value = user.email;
    document.getElementById("usRole").value = user.roleId;
    document.getElementById("usPlatform").value = user.platformId || "";
    document.getElementById("usBusiness").value = user.businessId || "";

    document.getElementById("usSubmit").textContent = "Update User";
};

