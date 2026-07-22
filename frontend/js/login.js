// Already-logged-in users skip straight to the dashboard
if (Auth.getToken()) window.location.href = "dashboard.html";

const form = document.getElementById("loginForm");
const errorBox = document.getElementById("loginError");
const loginBtn = document.getElementById("loginBtn");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  errorBox.style.display = "none";
  loginBtn.disabled = true;
  loginBtn.textContent = "Logging in…";

  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;

  try {
    const data = await api("/auth/login", { method: "POST", json: { email, password } });
    Auth.setSession(data.token, data.user);
    window.location.href = "dashboard.html";
  } catch (err) {
    errorBox.textContent = err.message;
    errorBox.style.display = "block";
  } finally {
    loginBtn.disabled = false;
    loginBtn.textContent = "Log in";
  }
});

document.getElementById("forgotLink").addEventListener("click", async (e) => {
  e.preventDefault();
  const email = document.getElementById("email").value.trim();
  if (!email) {
    errorBox.textContent = "Enter your email above first, then click 'Forgot password?'";
    errorBox.style.display = "block";
    return;
  }
  try {
    const res = await api("/auth/forgot-password", { method: "POST", json: { email } });
    errorBox.style.display = "none";
    alert(res.message);
  } catch (err) {
    errorBox.textContent = err.message;
    errorBox.style.display = "block";
  }
});
