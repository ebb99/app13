document.getElementById("loginForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const name = document.getElementById("name").value;
    const password = document.getElementById("password").value;

    // 🔐 Login
    const res = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ name, password })
    });

    const data = await res.json();

    if (!res.ok) {
        document.getElementById("loginError").textContent =
            data.error || "Login fehlgeschlagen";
        return;
    }

    // 📦 Session prüfen
    const sessionRes = await fetch("/api/session", {
        credentials: "include"
    });

    const session = await sessionRes.json();
    //const user = session.user.name;
    //console.log("Eingeloggt als:", session.user);
    if (!session.user) {
        document.getElementById("loginError").textContent =
            "Session-Fehler";
        return;
    }

    console.log("LOGIN OK:", session.user);

    // 🔀 Redirect
    if (session.user.role === "admin") {
        window.location.href = "/admin_dashboard.html";
    end
    } else {
        window.location.href = "/tipper_spiele.html";
    }



if (session.user.role === "admin") {
  window.location.href = "/admin_dashboard.html";
} else if (session.user.role === "familie") {
   window.location.href = "/familie.html";
} else {
  window.location.href = "/tipper_spiele.html";
}






});
