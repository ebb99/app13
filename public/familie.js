//const { text } = require("express");

console.log("✅ tipper_dashboard.js geladen");

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



// // ===============================
// // INIT
// // ===============================
document.addEventListener("DOMContentLoaded", async () => {
    try {
        await checkSession("familie");
        await name_ermitteln();
        //await ladeSpiele();

        // $("logoutBtn")?.addEventListener("click", logout);
        // $("tipper_spieleBtn")?.addEventListener("click", () => {
        //     window.location.href = "tipper_spiele.html";
        // });

    } catch (err) {
        console.error("❌ Zugriff verweigert", err);
        location.href = "/";
    }
});

// // Logout
// // ===============================
// async function logout() {
//     await api("/api/logout", { method: "POST" });
 
//     location.href = "/";
// }





// function zeigeMeldung(text, farbe) {
//     const el = document.getElementById("meldung");
//     el.textContent = text;
//     el.style.color = farbe;
// }

// function zeigeTestMeldung(text, farbe) {
//  const container = document.getElementById('testmeldung');
// //document.getElementById("output").textContent = JSON.stringify(spiele, null, 2);
// // 1. Neues Element für die farbige Gruppe erstellen
// const neueGruppe = document.createElement('div');
// neueGruppe.style.color = farbe; // Ihre Wunschfarbe
// neueGruppe.style.whiteSpace = "pre-line"; // Aktiviert die Erkennung von \n

// // 2. Variable Texte definieren
// let text1 = text;


// // 3. Texte mit \n (Newline) verknüpfen und zuweisen
// neueGruppe.textContent = `${text}\n`;
// // 4. Alles an den Hauptcontainer anhängen
// container.appendChild(neueGruppe);
// };

// function zeigeTestjson(data, farbe) {
//  const container = document.getElementById('testmeldung');
// const neueGruppe = document.createElement('div');
// neueGruppe.style.color = farbe; // Ihre Wunschfarbe
// neueGruppe.style.whiteSpace = "pre-line"; // Aktiviert die Erkennung von \n
// neueGruppe.textContent = JSON.stringify(data, null, 2);
// // 4. Alles an den Hauptcontainer anhängen
// container.appendChild(neueGruppe);
// };

// function TestMeldunglöschen() {
//     const el = document.getElementById("testmeldung");
//     el.innerHTML = "";
// }

// // async function ladeSpieleMitTipps() {
// //     const spiele = await api("/api/spiele");
// //     const tbody = $("tipTabelle");
// //     tbody.innerHTML = "";
// //     //zeigeTestMeldung(`${spiele} alle Spiele `, "blue");
    
// //     //const geplant = spiele.filter(s => s.statuswort === "geplant");
// //     const geplant = spiele.filter(s => new Date(s.anstoss) > new Date());

// //     //zeigeTestjson (spiele, "blue");
// //     if (geplant.length === 0) {
// //         tbody.innerHTML = `<tr><td>Keine geplanten Spiele</td></tr>`;
// //         //zeigeTestMeldung(`${geplant.length} Spiele geplant`, "green");
// //         return;
// //     }

// //     //zeigeTestMeldung(`${geplant.length} Spiele geladen`, "green")
    
// // const options = { 
// //   weekday: 'long',   // "Samstag"
// //   year: 'numeric',   // "2026"
// //   month: '2-digit',  // "01"
// //   day: '2-digit',    // "17"
// //   hour: '2-digit',   // "18"
// //   minute: '2-digit'  // "00"
// // };

// //     geplant.forEach(s => {
// //         // Zeile 1: Datum + Status
// //         const tr1 = document.createElement("tr");

// //  const textd = new Date(s.anstoss).toLocaleString("de-DE", options) + " Uhr";
// // // console.log(textd); // Ausgabe z.B.: "Samstag, 17.01.2026, 18:00 Uhr"
    

  
// //          tr1.innerHTML = `
// //             <td colspan="3">
// //                        ${textd}
// //                 | Status: <b>${s.statuswort}</b>
// //             </td>
// //         `;

// //       // Zeile 2: Heimverein + Tipp
// //         const tr2 = document.createElement("tr");
// //         const logoh = s.heimverein + "_logo.png";


// // heimLogoHtml = `<img src="${s.heimbild}" alt="${s.heimverein}" class="team-logo">`;


// //         tr2.innerHTML = `
// //             <td width="60%"><b>

// //             ${heimLogoHtml}
// //              ${s.heimverein}
// //              </b>
// //              </td>

// //             <td width="20%">Heim</td>



// //             <td width="20%">

// //                 <input type="number"
// //                        min="0"
// //                        data-spiel="${s.id}"
// //                        data-team="heim"
// //                        class="tippInput">
// //             </td>
// //         `;

// //         // Zeile 3: Gastverein + Tipp
// //         const tr3 = document.createElement("tr");
// //         const logog = s.gastverein + "_logo.png";
// // // let gastLogoHtml;
// // // if (s.gastbild) {
// //     gastLogoHtml = `<img src="${s.gastbild}" alt="${s.gastverein}" class="team-logo">`;
// // // } else {
// // //     gastLogoHtml = `<img src="/bilder/${logog}" alt="${s.gastverein}" class="team-logo">`;
// // // }
// //         tr3.innerHTML = `
// //             <td width="60%">
// //             <b>
// //                 ${gastLogoHtml}
// //                 ${s.gastverein}
// //             </b>
// //              </td>
// //             <td width="20%">Gast</td>
// //             <td width="20%">
           
// //                 <input type="number"
// //                        min="0"
// //                        data-spiel="${s.id}"
// //                        data-team="gast"
// //                        class="tippInput">
// //             </td>
// //         `;

// //         // optische Trennung
// //         const trSpacer = document.createElement("tr");
// //         trSpacer.innerHTML = `<td colspan="3">&nbsp;</td>`;

// //         tbody.append(tr1, tr2, tr3, trSpacer);
// //     });
// // }


// async function ladeSpieleMitTipps() {
//     const spiele = await api("/api/spiele");

//     const container = $("tipContainer"); // div statt tbody
//     container.innerHTML = "";

//     const geplant = spiele.filter(s => new Date(s.anstoss) > new Date());

//     if (geplant.length === 0) {
//         container.innerHTML = `<p>Keine geplanten Spiele</p>`;
//         return;
//     }

//     const options = { 
//         weekday: 'long',
//         year: 'numeric',
//         month: '2-digit',
//         day: '2-digit',
//         hour: '2-digit',
//         minute: '2-digit'
//     };

//     // 🔹 Spiele nach Gruppen sortieren
//     const gruppen = {};

//     geplant.forEach(s => {
//         const [order, name] = s.spielgruppe.split("_");

//         if (!gruppen[name]) {
//             gruppen[name] = {
//                 order: parseInt(order),
//                 spiele: []
//             };
//         }

//         gruppen[name].spiele.push(s);
//     });

//     // 🔹 Gruppen sortieren
//     const sortierteGruppen = Object.entries(gruppen)
//         .sort((a, b) => a[1].order - b[1].order);

//     // 🔹 Tabellen erzeugen
//     sortierteGruppen.forEach(([gruppenName, gruppe]) => {

//         const h3 = document.createElement("h3");
//         h3.textContent = gruppenName;
//         container.appendChild(h3);

//         const table = document.createElement("table");
//         table.classList.add("tipTabelle");

//         const tbody = document.createElement("tbody");

//         gruppe.spiele.forEach(s => {

//             const textd = new Date(s.anstoss).toLocaleString("de-DE", options) + " Uhr";

//             const tr1 = document.createElement("tr");
//             tr1.innerHTML = `
//                 <td colspan="3">
//                     ${textd} | Status: <b>${s.statuswort}</b>
//                 </td>
//             `;

//             const tr2 = document.createElement("tr");

//             const heimLogoHtml =
//                 `<img src="${s.heimbild}" alt="${s.heimverein}" class="team-logo">`;

//             tr2.innerHTML = `
//                 <td width="60%">
//                     <b>${heimLogoHtml} ${s.heimverein}</b>
//                 </td>
//                 <td width="20%">Heim</td>
//                 <td width="20%">
//                     <input type="number"
//                            min="0"
//                            value="${s.heimtipp ?? ""}"
//                            data-spiel="${s.id}"
//                            data-team="heim"
//                            class="tippInput">
//                 </td>
//             `;

//             const tr3 = document.createElement("tr");

//             const gastLogoHtml =
//                 `<img src="${s.gastbild}" alt="${s.gastverein}" class="team-logo">`;

//             tr3.innerHTML = `
//                 <td width="60%">
//                     <b>${gastLogoHtml} ${s.gastverein}</b>
//                 </td>
//                 <td width="20%">Gast</td>
//                 <td width="20%">
//                     <input type="number"
//                            min="0"
//                            value="${s.gasttipp ?? ""}"
//                            data-spiel="${s.id}"
//                            data-team="gast"
//                            class="tippInput">
//                 </td>
//             `;

//             const trSpacer = document.createElement("tr");
//             trSpacer.innerHTML = `<td colspan="3">&nbsp;</td>`;

//             tbody.append(tr1, tr2, tr3, trSpacer);
//         });

//         table.appendChild(tbody);
//         container.appendChild(table);
//     });
// }










// async function alleTippsSpeichern() {
//     const inputs = document.querySelectorAll(".tippInput");

//     // Map: spiel_id → { heimtipp, gasttipp }
//     const tipps = {};

//     inputs.forEach(input => {
//         const spielId = input.dataset.spiel;
//         const team = input.dataset.team;
//         const wert = input.value;

//         if (!tipps[spielId]) {
//             tipps[spielId] = {};
//         }

//         if (wert !== "") {
//             tipps[spielId][team + "tipp"] = Number(wert);
//         }
//     });

//     try {
//         for (const spielId in tipps) {
//             const t = tipps[spielId];

//             // nur speichern, wenn beide Werte vorhanden
//             if (t.heimtipp == null || t.gasttipp == null) continue;
// // console.log(` Speichere Tipp für Spiel ${spielId}: ${t.heimtipp} : ${t.gasttipp}`);
//             await api("/api/tips", {
//                 method: "POST",
//                 body: JSON.stringify({
//                     spiel_id: spielId,
//                     heimtipp: t.heimtipp,
//                     gasttipp: t.gasttipp
//                 })
//             });
//         }
//         ladeTipps();
//         $("meldung").textContent = "✅ Tipps gespeichert";
//         $("meldung").style.color = "green";

//     } catch (err) {
//         console.error(err);
//         $("meldung").textContent = "❌ Fehler beim Speichern";
//         $("meldung").style.color = "red";
//     }
// }






async function name_ermitteln(requiredRole = null) {
    const res = await fetch("/api/session", {
        credentials: "include"
    });

    if (!res.ok) {
        throw new Error("Session-Fehler");
    }

    const data = await res.json();

    if (!data.user) {
        throw new Error("Nicht eingeloggt");
    }

    if (requiredRole && data.user.role !== requiredRole) {
        throw new Error("Keine Berechtigung");
    }
    //console.log("Eingeloggt als:", data.user);
    $("benutzername").innerHTML = data.user.name;
    return data.user;
}




// // ===============================
// // Alle Tipps anzeigen
// // ===============================
// async function ladeTipps() {
//     const tips = await api("/api/tips");
//     const container = $("tipListe");

//     container.innerHTML = "";

//     const spieleMap = {};

//     tips.forEach(t => {
//         if (!spieleMap[t.spiel_id]) {
//             spieleMap[t.spiel_id] = {
//                 spiel: t,
//                 tips: []
//             };
//         }
//         spieleMap[t.spiel_id].tips.push(t);
//     });

//  Object.values(spieleMap)
//   .sort((a, b) => new Date(b.spiel.anstoss) - new Date(a.spiel.anstoss))
//   .forEach(gruppe => {

//     // Tipps: letzte zuerst
//     gruppe.tips.sort(
//       (a, b) => new Date(b.updated_at) - new Date(a.updated_at)
//     );

//     const div = document.createElement("div");
//     div.className = "spiel";

    
    
//     gruppe.spiel.statuswort === "beendet" ? "status-beendet" : "status-offen";
//     const statuswort = gruppe.spiel.statuswort;
//     const cssClass = getStatusClass(statuswort);
//     div.innerHTML = `
//     <strong>${gruppe.spiel.heimverein} – ${gruppe.spiel.gastverein}</strong>
//     <div class="status">
//         ${new Date(gruppe.spiel.anstoss).toLocaleString("de-DE")}
//         | Status: <span class="${cssClass}">
//             ${gruppe.spiel.statuswort}
//            </span>
//         | Ergebnis: ${gruppe.spiel.heimtore ?? "-"} :
//         ${gruppe.spiel.gasttore ?? "-"}


//     </div>
// `;







//     gruppe.tips.forEach(tipp => {
//       const row = document.createElement("div");
//       row.className = "tipp";
//       row.innerHTML = `
//         <span>${tipp.user_name}</span>
//         <span>${tipp.heimtipp} : ${tipp.gasttipp}</span>
//         <span>${tipp.punkte ?? 0} P</span>
//       `;
//       div.appendChild(row);
//     });

//     container.appendChild(div);
//   });

// }

// // ===============================
// // Rangliste
// // ===============================
// async function ladeRangliste() {
//     const data = await api("/api/rangliste");

//     const tbody = $("ranglisteBody");
//     tbody.innerHTML = "";
//       data.forEach((u, i) => {
//         const tr = document.createElement("tr");
//         tr.innerHTML = `
//             <td>${i + 1}</td>
//             <td>${u.name}</td>
//             <td>${u.punkte} / ${u.tipps_anzahl}             
//             </td>
//         `;
//         tbody.appendChild(tr);
//     });
// }
