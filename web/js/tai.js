// ---- API base configuration ----
// If you want to hardcode an API endpoint, set it here, e.g. "/tool/tai"
// Otherwise leave blank ("") to auto-detect relative to index.html
let API_BASE = "";

// Auto-detect: if API_BASE is not set manually
if (!API_BASE) {
  // Get current path, strip off /index.html if present
  const basePath = window.location.pathname.replace(/\/index\.html$/, "");
  API_BASE = basePath; // works for root ("/") or mounted paths ("/tool/tai")
}

let lastResults = null;

async function run() {
  const mode = document.getElementById("mode").value;
  const q = document.getElementById("q").value.trim();
  const resultsDiv = document.getElementById("results");
  resultsDiv.innerHTML = `<div class="alert alert-info">Loading…</div>`;

  try {
    let out;
    if (mode === "uuid_get") {
      out = await fetch(`get/${encodeURIComponent(q)}`).then(r => r.json());
    } else {
      let body = {};
      if (mode === "name") body = { name: q };
      if (mode === "uuid") body = { uuid: q };
      if (mode === "country") body = { country: q.toUpperCase() };

      out = await fetch(`query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
      }).then(r => r.json());
    }

    lastResults = out;
    document.getElementById("exportBtn").disabled = false;
    document.getElementById("results").innerHTML = Array.isArray(out) ? out.map(renderCard).join("") : renderCard(out);
  } catch (e) {
    resultsDiv.innerHTML = `<div class="alert alert-danger">${e.message}</div>`;
    document.getElementById("exportBtn").disabled = true;
  }
}

function renderCard(item) {
  if (!item) return "";
  const synonyms = item.meta?.synonyms?.length ? `<p><strong>Aliases:</strong> ${item.meta.synonyms.join(", ")}</p>` : "";
  const country = item.meta?.country ? `<span class="badge bg-secondary">${item.meta.country}</span>` : "";
  const refs = item.meta?.refs?.length
    ? `<p><strong>References:</strong><br>` +
      item.meta.refs
        .map(r => `<a href="${r}" target="_blank" class="d-block">${r}</a>`)
        .join("") +
      `</p>`
    : "";

  return `
    <div class="card mb-3">
      <div class="card-body">
        <h5 class="card-title">${item.value || item.name || "Unknown"} ${country}</h5>
        <h6 class="card-subtitle mb-2 text-muted">${item.uuid}</h6>
        <p class="card-text">${item.description || ""}</p>
        ${synonyms}
        ${refs}
      </div>
    </div>`;
}

function exportJSON() {
  if (!lastResults) return;
  const blob = new Blob([JSON.stringify(lastResults, null, 2)], { type: "application/json" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "tais-results.json";
  a.click();
}
