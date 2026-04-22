console.log("✅ planung.js geladen");

// ===============================
// Helper
// ===============================
async function api(url, options = {}) {
    const res = await fetch(url, {
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        ...options
    });

    if (!res.ok) {
        const txt = await res.text();
        throw new Error(txt || res.statusText);
    }

    return res.status === 204 ? null : res.json();
}

function $(id) {
    return document.getElementById(id);
}

// function getStatusClass(statuswort) {
//     const mapping = {
//         geplant: "status-geplant",
//         live: "status-live",
//         beendet: "status-beendet",
//         ausgewertet: "status-ausgewertet"
//     };

//     return mapping[statuswort] || "";  // falls etwas Unerwartetes kommt
// }

// ===============================
// INIT
// ===============================
document.addEventListener("DOMContentLoaded", async () => {
    try {
        // await checkSession("tipper");
        // await name_ermitteln();
        // //await ladeSpiele();
        // await ladeTipps();
        // await ladeRangliste();
        await lade_planung();
        // $("Button1")?.addEventListener("click", planung_neu);
       // $("saveAllTips").addEventListener("click", tippSpeichern);
        // $("logoutBtn")?.addEventListener("click", logout);
        // $("tipper_spieleBtn")?.addEventListener("click", () => {
        //     window.location.href = "tipper_spiele.html";
        // });

        //    //await ladeGeplanteSpiele();
       
        // // $("saveAllTips").addEventListener("click", alleTippsSpeichern);
        // $("saveAllTips").addEventListener("click", alleTippsSpeichern);
        // //console.log("✅ Tipper Dashboard bereit");

    } catch (err) {
        console.error("❌ Zugriff verweigert", err);
        location.href = "/";
    }
});

async function runPython() {
    const resultEl = document.getElementById("result");
    resultEl.innerText = "Lädt...";

    try {
        const res = await fetch("/run-job", {
            method: "POST"
        });

        console.log(res.status);

        const data = await res.json();
        console.log(data);

        if (data.status === "ok") {
            resultEl.innerText = "✅ Erfolgreich!";
        } else {
            resultEl.innerText = "❌ Fehler: " + (data.message || "Unbekannt");
        }

    } catch (err) {
        console.error(err);
        resultEl.innerText = "❌ Netzwerkfehler";
    }
}

async function lade_planung() {
    const res = await fetch("/api/spiele/planung");
    spiele = await res.json();

    const tbody = document.getElementById("planTable");
    tbody.innerHTML = "";

    spiele.forEach(s => {
            tbody.innerHTML += `
                <tr>
                    <td>${s.id}</td>
                    <td>${s.datum}</td>
                    <td>${s.zeit}</td>
                    <td>${s.heimverein}</td>
                    <td>${s.gastverein}</td>
                    <td>${s.score}</td>
                    <td><input type="checkbox" class="spiel-checkbox" data-id="${s.id}"></td>
    
                </tr>
            `;
        });    
}
async function planung_neu() {
    // const res = await fetch("/api/spiele/planung");
    // spiele = await res.json();

    const tbody = document.getElementById("planTable");
    tbody.innerHTML = "";
    alert("Planung neu")
    // spiele.forEach(s => {
    //     tbody.innerHTML += `
    //         <tr>
    //             <td>${s.id}</td>
    //             <td>${s.spielbeginn_formatiert}</td>
    //             <td>${s.heim_name}</td>
    //             <td>${s.gast_name}</td>
    //             <td><input id="home_${s.id}" type="number" min="0" value="${s.heimtore ?? ""}"></td>
    //             <td><input id="gast_${s.id}" type="number" min="0" value="${s.gasttore ?? ""}"></td>
    //         </tr>
    //     `;
    // });
}
