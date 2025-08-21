const API_BASE = "http://127.0.0.1:8000/api";
const hostSelect = document.getElementById("hostSelect");
const refreshBtn = document.getElementById("refreshBtn");
const tsEl = document.getElementById("ts");
const tbody = document.getElementById("tbody");
let currentData = [];

async function fetchJSON(url) {
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

async function loadHosts() {
  const data = await fetchJSON(`${API_BASE}/hosts/`);
  hostSelect.innerHTML = "";
  data.forEach((h) => {
    const opt = document.createElement("option");
    opt.value = h.hostname;
    opt.textContent = h.hostname;
    hostSelect.appendChild(opt);
  });
}

function fmtCPU(v) {
  return (v ?? 0).toFixed(1);
}
function fmtRSS(v) {
  return v ? (v / 1024 / 1024).toFixed(1) : "0.0";
}

function renderRows() {
  tbody.innerHTML = "";
  currentData.forEach((p) => {
    const tr = document.createElement("tr");
    const hasCmdline = p.cmdline && p.cmdline.length > 0;

    tr.innerHTML = `
      <td class="mono">${p.id}</td>
      <td class="mono">${p.pid}</td>
      <td>${p.name || '<span class="muted">(unknown)</span>'} ${
      hasCmdline
        ? '<span class="toggle-btn" data-pid="' + p.pid + '">[+]</span>'
        : ""
    }</td>
      <td>${fmtCPU(p.cpu_percent)}%</td>
      <td class="mono">${fmtRSS(p.memory_rss)}</td>
      <td class="mono muted">${p.ppid ?? ""}</td>
    `;
    tbody.appendChild(tr);

    if (hasCmdline) {
      const exeArgs = p.cmdline
        .split(" ")
        .filter((arg) => arg.toLowerCase().endsWith(".exe"));
      //   const exeArgs = p.cmdline.split(" ").filter(Boolean);

      if (exeArgs.length > 0) {
        const subRow = document.createElement("tr");
        subRow.classList.add("cmdline-row", "child-of-" + p.pid);
        subRow.style.display = "none";
        let innerTable = `
      <table style="width:50%; border-collapse:collapse; font-size:13px;">
        <thead>
          <tr style="background:#f0f5ff; text-align:left;">
            <th style="padding:6px; border:1px solid #d7dee9;">#</th>
            <th style="padding:6px; border:1px solid #d7dee9;">Executable Path</th>
          </tr>
        </thead>
        <tbody>
          ${exeArgs
            .map((arg, idx) => {
              const truncated =
                arg.length > 250 ? arg.substring(0, 250) + "…" : arg;
              return `
                <tr>
                  <td style="padding:6px; border:1px solid #d7dee9;">${
                    idx + 1
                  }</td>
                  <td style="padding:6px; border:1px solid #d7dee9;" class="mono">${truncated}</td>
                </tr>`;
            })
            .join("")}
        </tbody>
      </table>
    `;

        subRow.innerHTML = `<td colspan="5">${innerTable}</td>`;
        tbody.appendChild(subRow);
      }
    }
  });
}

tbody.addEventListener("click", (e) => {
  if (e.target.classList.contains("toggle-btn")) {
    const pid = e.target.dataset.pid;
    const childRows = tbody.querySelectorAll(".child-of-" + pid);
    const expanded = e.target.textContent === "[-]";
    childRows.forEach(
      (r) => (r.style.display = expanded ? "none" : "table-row")
    );
    e.target.textContent = expanded ? "[+]" : "[-]";
  }
});

async function refresh() {
  const host = hostSelect.value;
  if (!host) return;
  const data = await fetchJSON(
    `${API_BASE}/hosts/${encodeURIComponent(host)}/latest/`
  );
  currentData = Array.isArray(data.processes) ? data.processes.slice() : [];
  tsEl.textContent = `Snapshot: ${new Date(data.taken_at).toLocaleString()}`;
  renderRows();
}

refreshBtn.addEventListener("click", refresh);
(async function init() {
  await loadHosts();
  if (hostSelect.options.length) hostSelect.selectedIndex = 0;
  await refresh();
  //   setInterval(refresh, 10000);
})();
