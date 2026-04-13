console.log("✅ admin_dashboard.js geladen");
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

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function speicherProzess() {
    $("meldung").textContent = "Spiel gespeichert";
    $("meldung").style.color = "green";

    // Jetzt funktioniert der Aufruf, da die Funktion oben definiert wurde
    await sleep(1000);

    $("meldung").textContent = "";
}





// ===============================
// INIT
// ===============================
document.addEventListener("DOMContentLoaded", () => {

    ladeVereine();
    ladeUser();
    ladeGruppen();
    ladeSpiele();

    $("logoutBtn")?.addEventListener("click", logout);

    $("saveVerein")?.addEventListener("click", vereinSpeichern);
    $("deleteVerein")?.addEventListener("click", vereinLoeschen);

    $("saveGruppe")?.addEventListener("click", gruppeSpeichern);
    $("deleteGruppe")?.addEventListener("click", gruppeLoeschen);

    $("saveSpiel")?.addEventListener("click", spielSpeichern);
    $("deleteSpiel")?.addEventListener("click", spielLoeschen);
    $("saveErgebnis")?.addEventListener("click", ergebnisSpeichernUndAuswerten);
    $("userForm").addEventListener("submit", userSpeichern);
   

});
// ===============================
// Logout
// ===============================
async function logout() {
    await api("/api/logout", { method: "POST" });
    location.href = "/";
}

function $(id) {
    return document.getElementById(id);
}

// synchronisiert mit app1 bis hierher

// ===============================
// Gruppen
// ===============================

async function ladeGruppen() {
    const gruppen = await api("/api/gruppen");
    $("allegruppen").innerHTML = "";
    const datalist = $("gruppenliste");
    datalist.innerHTML = "";

    gruppen.forEach(g => {
        $("allegruppen").appendChild(new Option(g.gruppenname, g.id));
        $("gruppeSelect").appendChild(new Option(g.gruppenname, g.id));    
    });

    gruppen.forEach(g => {
        const option = document.createElement("option");
        option.value = g.gruppenname;   // angezeigter Text
        option.dataset.id = g.id;       // Gruppen-ID speichern
        datalist.appendChild(option);
    });
}



async function gruppeSpeichern() {
    // alert("Gruppe speichern: " + $("gruppeInput").value); 
       const name = $("gruppeInput").value.trim();
    if (!name) return alert("Name fehlt"); 
    alert("Speichere Gruppe: " + name); 
    await api("/api/gruppen", {
        method: "POST",
        headers: {
        "Content-Type": "application/json"
        },
         body: JSON.stringify({ gruppenname: name })
    });
    // alert("✅ Gruppe gespeichert");
    $("gruppeInput").value = "";
    ladeGruppen();
}

function getGruppeId(inputId) {
    const value = $(inputId).value;
    const option = [...$("gruppenliste").options]
        .find(o => o.value === value);
    return option ? option.dataset.id : null;
}

async function gruppeLoeschen() {
    // const id = $("gruppenSelect").value;
    const id = getGruppeId("gruppenSelect");
    const name = $("gruppenSelect").value;
    alert(`Lösche Gruppe "${name}" (ID: ${id})`);
//   console.log("Lösche Gruppe mit ID:", id);
    if (!id) return; 
    await api(`/api/gruppen/${id}`, { method: "DELETE" });
    ladeGruppen();       
}








async function vereinSpeichern() {
    const name = $("vereinInput").value.trim();
    const logo = $("logoInput").value.trim();
    if (!name) return alert("Name fehlt");

    await api("/api/vereine", {
        method: "POST",
         body: JSON.stringify({ vereinsname: name, url: logo })
    });
    alert("✅ Verein gespeichert");
    $("vereinInput").value = "";
    $("logoInput").value = "";
    ladeVereine();
}

function getHeimId(inputId) {
    const value = $(inputId).value;
    const option = [...$("heimselect").options]
        .find(o => o.value === value);
    return option ? option.dataset.id : null;
}
 
function getGastId(inputId) {
    const value = $(inputId).value;
    const option = [...$("gastselect").options]
        .find(o => o.value === value);
    return option ? option.dataset.id : null;
}


async function ladeVereine() {
    const vereine = await api("/api/vereine");

    const datalist = $("vereineList");
    datalist.innerHTML = "";

    vereine.forEach(v => {
        const option = document.createElement("option");
        option.value = v.vereinsname;   // angezeigter Text
        option.dataset.id = v.id;       // Vereins-ID speichern
        datalist.appendChild(option);
    });


        $("allevereine").innerHTML = "";
    vereine.forEach(v => {
        $("allevereine").appendChild(new Option(v.vereinsname, v.id));
    });
}

function getVereinId(inputId) {
    const value = $(inputId).value;
    const option = [...$("vereineList").options]
        .find(o => o.value === value);
    return option ? option.dataset.id : null;
}

async function vereinLoeschen() {
    // const id = $("gruppenSelect").value;
    const id = getVereinId("vereineselect");
    const name = $("vereineselect").value;
    alert(`Lösche Verein "${name}" (ID: ${id})`);
//   console.log("Lösche Verein mit ID:", id);
    if (!id) return; 
    await api(`/api/vereine/${id}`, { method: "DELETE" });
    ladeVereine();       
}


// ===============================
// Spiele
// ===============================
async function ladeSpiele() {
    const spiele = await api("/api/spiele");
    console.log("👂 /api/spiele - Spiele:", spiele);
    $("spieleSelect").innerHTML = "";
    spiele.forEach(s => {
    const text = `
    ${s.spielgruppe}:
    ${new Date(s.anstoss).toLocaleString("de-DE", {dateStyle: "short",timeStyle: "short",})}
     ${s.heimverein} : ${s.gastverein}, (${s.statuswort})

    `;
    $("spieleSelect").appendChild(new Option(text, s.id));
    });
}


async function spielSpeichern() {

    const heimName = $("heimInput").value;
    const gastName = $("gastInput").value;
    const gruppeName = $("gruppeSelect").selectedOptions[0]?.text;
    const gruppeId = $("gruppeSelect").value;
    const anstoss = $("anstosszeitInput").value;

    if (!heimName || !gastName) {
        return alert("Bitte Heim- und Gastverein wählen");
    }

    if (heimName === gastName) {
        return alert("Heim- und Gastverein dürfen nicht identisch sein");
    }

    // Vereine laden
    const vereine = await api("/api/vereine");

    const heimVerein = vereine.find(v => v.vereinsname === heimName);
    const gastVerein = vereine.find(v => v.vereinsname === gastName);

    if (!heimVerein || !gastVerein) {
        return alert("Verein nicht in der Liste gefunden");
    }

    const heimbild = heimVerein.url;
    const gastbild = gastVerein.url;

   
    
console.log({
    spielgruppe: gruppeName,
    anstoss,
    heimverein: heimName,
    gastverein: gastName,
    heimbild,
    gastbild
});


    await api("/api/spiele", {
        method: "POST",
        body: JSON.stringify({
            spielgruppe: gruppeName,
            anstoss,
            heimverein: heimName,
            gastverein: gastName,
            heimbild,
            gastbild,
            heimtore: 0,
            gasttore: 0,
            statuswort: "geplant"
        })
    });

    alert(`Spiel angelegt:\n${heimName} vs ${gastName}`);
    ladeSpiele();
}



async function spielLoeschen() {
    const id = $("spieleSelect").value;
    if (!id) return;
    console.log("Lösche Spiel mit ID:", id);
    await api(`/api/spiele/${id}`, { method: "DELETE" });
    ladeSpiele();
}

async function ergebnisSpeichernUndAuswerten() {
    const id = $("spieleSelect").value;
    if (!id) return alert("Spiel wählen");

    const heimtore = Number($("heimtoreInput").value);
    const gasttore = Number($("gasttoreInput").value);

    try {
        const res = await api(`/api/spiele/${id}/ergebnis`, {
            method: "PATCH",
            body: JSON.stringify({ heimtore, gasttore })
        });

        alert("✅ Ergebnis gespeichert & Punkte berechnet");
        ladeSpiele();

    } catch (err) {
        alert("❌ Fehler bei der Auswertung");
        console.error(err);
    }
}



/// ===============================
// Benutzerverwaltung
// ===============================
async function ladeUser() {
    try {
        const res = await fetch("/api/users", {
            credentials: "include"
        });

        if (!res.ok) {
            throw new Error("User laden fehlgeschlagen");
        }

        const users = await res.json();

        const tbody = $("userTable");
        tbody.innerHTML = "";

        users.forEach(u => {
            const tr = document.createElement("tr");

            tr.innerHTML = `
                <td>${u.name}</td>
                <td>${u.role}</td>
                <td>
                    <button class="editBtn">Bearbeiten</button>
                    <button class="deleteBtn">Löschen</button>
                </td>
            `;

            // ✏️ Bearbeiten
            tr.querySelector(".editBtn").addEventListener("click", () => {
                userBearbeiten(u);
            });

            // 🗑️ Löschen
            tr.querySelector(".deleteBtn").addEventListener("click", async () => {
                if (!confirm(`User ${u.name} löschen?`)) return;

                const delRes = await fetch(`/api/users/${u.id}`, {
                    method: "DELETE",
                    credentials: "include"
                });

                if (!delRes.ok) {
                    alert("Fehler beim Löschen");
                    return;
                }

                ladeUser();
            });

            tbody.appendChild(tr);
        });

    } catch (err) {
        console.error("❌ ladeUser:", err);
        alert("Benutzer konnten nicht geladen werden");
    }
}

async function userAnlegen(e) {
    e.preventDefault();

    const name = $("userName").value.trim();
    const password = $("userPassword").value;
    const role = $("userRole").value;

    if (!name || !password) {
        return alert("Name und Passwort erforderlich");
    }

    const res = await fetch("/api/users", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, password, role })
    });

    if (!res.ok) {
        const t = await res.text();
        alert("Fehler: " + t);
        return;
    }

    $("userForm").reset();
    ladeUser();
}

function userFormReset() {
    $("userForm").reset();
    $("userId").value = "";
}

function userBearbeiten(u) {
    $("userId").value = u.id;
    $("userName").value = u.name;
    $("userRole").value = u.role;

    $("userPassword").value = ""; // wichtig!
}

async function userAendern(e) {
    e.preventDefault();

    const id = $("userId").value;        // wichtig: bestehende ID
    const name = $("userName").value.trim();
    const password = $("userPassword").value;

    if (!id || !name) {
        return alert("ID und Name erforderlich");
    }

    const res = await fetch(`/api/users/${id}`, {
        method: "PUT", // oder "PATCH" je nach API
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, password })
    });

    if (!res.ok) {
        const t = await res.text();
        alert("Fehler: " + t);
        return;
    }

    $("userForm").reset();
    ladeUser();
}

async function userSpeichern(e) {
    e.preventDefault();

    const id = $("userId").value;
    const name = $("userName").value.trim();
    const password = $("userPassword").value;
    const role = $("userRole").value;

    if (!name) {
        return alert("Name erforderlich");
    }

    const body = {
        name,
        role,
        password // ⚠️ wird bewusst IMMER überschrieben
    };

    const url = id ? `/api/users/${id}` : "/api/users";
    const method = id ? "PUT" : "POST";

    const res = await fetch(url, {
        method,
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
    });

    if (!res.ok) {
        const t = await res.text();
        alert("Fehler: " + t);
        return;
    }

    userFormReset();
    ladeUser();
}





async function ladeRangliste() {
    const daten = await api("/api/rangliste");

    const tbody = $("ranglisteBody");
    tbody.innerHTML = "";

    daten.forEach((u, i) => {
        tbody.innerHTML += `
            <tr>
                <td>${i + 1}</td>
                <td>${u.name}</td>
                <td>tips ${u.punkte}</td>

            </tr>
        `;
    });
}
