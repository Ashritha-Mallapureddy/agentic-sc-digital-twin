"""Write the page a recruiter opens. The numbers come from cbam_desk."""

from __future__ import annotations

import json
from pathlib import Path

from cbam_desk import CBAM_FACTOR, CERTIFICATE_PRICE, FERTILISER_MARKUP, LINES, MARKUP

ROOT = Path(__file__).resolve().parents[1]


def payload() -> dict:
    return {
        "price": CERTIFICATE_PRICE,
        "factor": {str(year): value for year, value in CBAM_FACTOR.items()},
        "markup": {str(year): value for year, value in MARKUP.items()},
        "fert": FERTILISER_MARKUP,
        "lines": [
            {
                "id": line.id,
                "good": line.good,
                "cn": line.cn,
                "sector": line.sector,
                "origin": line.origin,
                "customer": line.customer,
                "promise": line.promise,
                "tonnes": line.tonnes,
                "benchmark": line.benchmark,
                "country_default": line.country_default,
                "default_note": line.default_note,
                "benchmark_note": line.benchmark_note,
                "slices": [
                    {
                        "id": item.id,
                        "tier": item.tier,
                        "role": item.role,
                        "name": item.name,
                        "place": item.place,
                        "actual": item.actual,
                        "default_2026": item.default_2026,
                        "initial": item.initial,
                    }
                    for item in line.slices
                ],
            }
            for line in LINES
        ],
    }


HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Agentic CX desk · Ashritha Mallapureddy</title>
<style>
  :root { --ink:#1c2430; --navy:#0e1c2f; --line:#e3e8ef; --paper:#f4f6f8; --green:#0f7b4c; --amber:#9a6700; --red:#9f1239; }
  * { box-sizing: border-box; }
  body { margin:0; background:var(--paper); color:var(--ink); font-family:"Segoe UI", sans-serif; line-height:1.45; }
  .shell { display:grid; grid-template-columns: 250px 1fr; min-height:100vh; }
  nav { background:var(--navy); color:#e7edf5; padding:22px 18px; }
  nav h1 { font-size:18px; margin:0 0 4px; font-weight:650; }
  nav p { color:#b7c3d4; font-size:13px; margin:0 0 16px; }
  nav label { display:block; font-size:12px; letter-spacing:.04em; text-transform:uppercase; color:#b7c3d4; margin:14px 0 6px; }
  select, button { font:inherit; }
  select { width:100%; background:#16324f; color:white; border:1px solid #2a4a6d; padding:8px; }
  nav button { display:block; width:100%; text-align:left; background:transparent; color:#e7edf5; border:0; padding:10px 8px; margin-top:4px; cursor:pointer; }
  nav button.on { background:#16324f; }
  main { padding:28px 32px 48px; max-width:1080px; }
  h2 { margin:0 0 8px; font-weight:650; letter-spacing:-.02em; }
  .lead { margin:0 0 16px; max-width:760px; }
  .kpis { display:grid; grid-template-columns:repeat(4,1fr); gap:10px; margin:14px 0; }
  .kpi, .card, table { background:white; }
  .kpi { border-top:3px solid var(--navy); padding:12px 14px; }
  .kpi span { display:block; color:#5c6775; font-size:12px; }
  .kpi b { font-size:26px; font-weight:650; }
  .card { border:1px solid var(--line); padding:14px 16px; margin:12px 0; }
  .card.high { border-left:4px solid var(--red); }
  table { width:100%; border-collapse:collapse; font-size:14px; }
  th, td { text-align:left; padding:8px 10px; border-bottom:1px solid var(--line); vertical-align:top; }
  th { color:#5c6775; font-weight:600; }
  .tiers { display:grid; gap:10px; }
  .row { display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:10px; }
  .node { background:white; border:1px solid var(--line); padding:12px; }
  .node b { display:block; }
  .ok { color:var(--green); } .wait { color:var(--amber); } .bad { color:var(--red); }
  button.go { background:var(--navy); color:white; border:0; padding:8px 10px; cursor:pointer; margin-top:8px; }
  button.link { background:transparent; color:var(--navy); border:0; padding:0; cursor:pointer; text-decoration:underline; }
  .note { color:#5c6775; font-size:13px; }
  @media (max-width:800px) { .shell { grid-template-columns:1fr; } .kpis { grid-template-columns:1fr 1fr; } }
</style>
</head>
<body>
<div class="shell">
  <nav>
    <h1>Agentic CX desk</h1>
    <p>Linea Automotive GmbH · Düsseldorf · sample, not a filing and not an employer system</p>
    <label>Declaration year</label>
    <select id="year"></select>
    <label>Review</label>
    <button id="nav-decision" class="on">Decision</button>
    <button id="nav-customers">Customer promises</button>
    <button id="nav-chain">Supplier chain</button>
    <button id="nav-agents">Agents</button>
  </nav>
  <main id="main"></main>
</div>
<script>
const DATA = __DATA__;
const state = {
  page: "decision",
  year: 2026,
  line: DATA.lines[0].id,
  verified: new Set(DATA.lines.flatMap(line => line.slices.filter(item => item.initial === "verified").map(item => item.id)))
};
const euro = value => "€" + Math.round(value).toLocaleString("en-IE");
const markup = (sector, year) => sector === "Fertilisers" ? DATA.fert : DATA.markup[year];
const sliceValue = (item, line) => {
  if (state.verified.has(item.id)) return item.actual;
  return item.default_2026 * (1 + markup(line.sector, state.year)) / (1 + markup(line.sector, 2026));
};
const intensity = line => line.slices.reduce((sum, item) => sum + sliceValue(item, line), 0);
const marked = line => line.country_default * (1 + markup(line.sector, state.year));
const cost = (embedded, line) => Math.max(0, embedded - DATA.factor[state.year] * line.benchmark) * line.tonnes * DATA.price;
const fullSet = line => new Set(line.slices.map(item => item.id));
const costMode = (line, mode) => {
  const was = state.verified;
  if (mode === "full") state.verified = fullSet(line);
  const embedded = mode === "default" ? marked(line) : intensity(line);
  const value = cost(embedded, line);
  state.verified = was;
  return value;
};
function position(line) {
  const open = line.slices.filter(item => !state.verified.has(item.id));
  const dateOpen = open.some(item => item.tier === 1);
  const priceOpen = open.length > 0;
  let probability, impact, complaint;
  if (!priceOpen) { probability = 1; impact = 2; complaint = "No open complaint. The quoted price can stand."; }
  else if (dateOpen && open.some(item => item.initial === "unknown")) { probability = 4; impact = 5; complaint = "The customer cannot be given a firm date or a firm price."; }
  else if (line.tonnes >= 500) { probability = 3; impact = 5; complaint = "A certificate surcharge would change the order after the promise."; }
  else { probability = 3; impact = 3; complaint = "The price stays open until the missing installation is verified."; }
  const score = probability * impact;
  return { delivery: dateOpen ? "Open" : "Held", price: priceOpen ? "Open" : "Firm", complaint, score, band: score >= 15 ? "High" : score >= 8 ? "Medium" : "Low" };
}
function actions() {
  const rows = [];
  for (const line of DATA.lines) {
    for (const item of line.slices) {
      if (state.verified.has(item.id)) continue;
      const before = cost(intensity(line), line);
      state.verified.add(item.id);
      const after = cost(intensity(line), line);
      state.verified.delete(item.id);
      const euros = before - after;
      if (euros <= 1) continue;
      rows.push({ ...item, line, euros, verb: item.initial === "unknown" ? "Name the installation and verify it" : "Obtain the verifier's report" });
    }
  }
  rows.sort((a, b) => b.euros - a.euros);
  return rows;
}
function book(mode) {
  return DATA.lines.reduce((sum, line) => sum + costMode(line, mode), 0);
}
const findLine = id => DATA.lines.find(line => line.id === id);
function draw() {
  document.querySelectorAll("nav button").forEach(button => button.classList.toggle("on", button.id === "nav-" + state.page));
  const openPrice = DATA.lines.filter(line => position(line).price === "Open").length;
  const openDate = DATA.lines.filter(line => position(line).delivery === "Open").length;
  const today = book("today");
  const full = book("full");
  const main = document.getElementById("main");
  if (state.page === "decision") {
    const top = DATA.lines.map(line => ({ line, pos: position(line) })).sort((a, b) => b.pos.score - a.pos.score || b.line.tonnes - a.line.tonnes)[0];
    const act = actions().find(item => item.line.id === top.line.id);
    main.innerHTML = `
      <h2>Decision for the customer-experience review</h2>
      <p class="lead">One page for leadership. The customer was promised a date and a price. In 2026 the price can break when an imported good — steel, fertiliser, aluminium, cement or hydrogen — still has an unverified installation behind it. The certificate is paid either way. The mark-up is what turns the quote into an order change.</p>
      <div class="kpis">
        <div class="kpi"><span>Promises with an open price</span><b>${openPrice} of ${DATA.lines.length}</b></div>
        <div class="kpi"><span>Promises with an open date</span><b>${openDate} of ${DATA.lines.length}</b></div>
        <div class="kpi"><span>Mark-up still in the book</span><b>${euro(today - full)}</b></div>
        <div class="kpi"><span>Chain today</span><b>${euro(today)}</b></div>
      </div>
      <p class="note">Open price is an order change (Auftragsänderung). Open date is the delivery promise (Liefertreue). A surcharge after the order is the complaint (Reklamation). Risk score is probability × impact.</p>
      <div class="card high">
        <b>Workshop decision · ${top.line.id} · risk ${top.pos.score} ${top.pos.band}</b>
        <p>${top.line.customer}. ${top.line.promise}. ${top.pos.complaint}</p>
        <p>${act ? "On this account, " + act.verb.toLowerCase() + ": " + act.name + ". That removes " + euro(act.euros) + " of mark-up. Owner: the CX PMO analyst. Do not confirm this customer's price until that installation is verified." : "Every installation on this account is verified. Confirm the price."}</p>
        ${act ? `<button class="go" id="do-top">Record ${act.name} as verified</button>` : ""}
      </div>
      ${table()}`;
    const go = document.getElementById("do-top");
    if (go && act) go.onclick = () => { state.verified.add(act.id); draw(); };
  } else if (state.page === "customers") {
    main.innerHTML = `<h2>Customer promises</h2><p class="lead">Each customs line is a promise. Held means the plant on the invoice is verified, so the date can stand. Firm means every installation behind it is verified, so the quoted price can stand.</p>${table()}`;
  } else if (state.page === "chain") {
    const line = findLine(state.line);
    const pos = position(line);
    const options = DATA.lines.map(item => `<option value="${item.id}" ${item.id === line.id ? "selected" : ""}>${item.id} · ${item.good} · ${item.customer}</option>`).join("");
    const tiers = [1, 2, 3].map(tier => {
      const group = line.slices.filter(item => item.tier === tier);
      if (!group.length) return "";
      const title = tier === 1 ? "Tier 1 · the plant on the invoice" : tier === 2 ? "Tier 2 · precursors" : "Tier 3 · extraction the importer does not contract";
      const cards = group.map(item => {
        const known = state.verified.has(item.id);
        const klass = known ? "ok" : item.initial === "unknown" ? "bad" : "wait";
        const label = known ? "Verified actual" : item.initial === "unknown" ? "Installation unknown" : "Named, not verified";
        const button = known ? "" : `<button class="go" data-id="${item.id}">${item.initial === "unknown" ? "Name it and use the actual" : "Attach the verifier report"}</button>`;
        return `<div class="node"><span class="note">${item.role}</span><b>${item.name}</b><span class="note">${item.place}</span><div>${sliceValue(item, line).toFixed(3)} tCO2e/t</div><div class="${klass}">${label}</div>${button}</div>`;
      }).join("");
      return `<h3>${title}</h3><div class="row">${cards}</div>`;
    }).join("");
    main.innerHTML = `
      <h2>Supplier chain</h2>
      <p class="lead">The invoice names tier 1. The certificate also depends on the coke, the coal, the ore or the gas behind that plant. Until that installation is verified, its slice stays on the marked country default.</p>
      <label>Line</label><select id="line">${options}</select>
      <div class="kpis">
        <div class="kpi"><span>Delivery promise</span><b>${pos.delivery}</b></div>
        <div class="kpi"><span>Price promise</span><b>${pos.price}</b></div>
        <div class="kpi"><span>Embedded emissions used</span><b>${intensity(line).toFixed(2)}</b></div>
        <div class="kpi"><span>Certificate today</span><b>${euro(cost(intensity(line), line))}</b></div>
      </div>
      <p class="note">${line.default_note} ${line.benchmark_note || ""}</p>
      <div class="tiers">${tiers}</div>`;
    document.getElementById("line").onchange = event => { state.line = event.target.value; draw(); };
    main.querySelectorAll("button[data-id]").forEach(button => button.onclick = () => { state.verified.add(button.dataset.id); draw(); });
  } else {
    const rows = actions();
    const unnamed = DATA.lines.flatMap(line => line.slices).filter(item => item.initial === "unknown" && !state.verified.has(item.id)).length;
    const list = rows.map(row => `<div class="card"><b>${row.verb}</b><div>${row.line.id} ${row.line.good} · ${row.line.customer}</div><div class="note">${row.name} · ${row.place} · tier ${row.tier}</div><div>Removes ${euro(row.euros)} · ${position(row.line).complaint}</div><button class="go" data-id="${row.id}">Record it as verified</button></div>`).join("");
    main.innerHTML = `
      <h2>Agents</h2>
      <p class="lead">Four agents read the same book. They do not remove a certificate the verified figure still requires. They remove the mark-up that exists only because an installation is missing, and they say which customer promise that mark-up is holding open.</p>
      <div class="kpis">
        <div class="kpi"><span>Customs reader</span><b>${DATA.lines.length} lines</b></div>
        <div class="kpi"><span>Chain scout</span><b>${unnamed} unnamed</b></div>
        <div class="kpi"><span>Emissions clerk</span><b>${euro(today)}</b></div>
        <div class="kpi"><span>Certificate desk</span><b>${rows.length} actions</b></div>
      </div>
      ${list || `<div class="card"><b>The book is verified.</b><p>The remaining certificate is the actual embedded emissions.</p></div>`}
      <button class="go" id="reset">Reset to the evidence the book started with</button>`;
    main.querySelectorAll("button[data-id]").forEach(button => button.onclick = () => { state.verified.add(button.dataset.id); draw(); });
    document.getElementById("reset").onclick = () => {
      state.verified = new Set(DATA.lines.flatMap(line => line.slices.filter(item => item.initial === "verified").map(item => item.id)));
      draw();
    };
  }
  main.querySelectorAll("button.link").forEach(button => button.onclick = () => { state.page = "chain"; state.line = button.dataset.line; draw(); });
}
function table() {
  const body = DATA.lines.map(line => {
    const pos = position(line);
    return `<tr><td>${line.id}<br><span class="note">${line.good} · ${line.cn}</span></td><td>${line.customer}<br><span class="note">${line.promise}</span></td><td>${pos.delivery}</td><td>${pos.price}</td><td>${pos.band} ${pos.score}</td><td>${euro(cost(intensity(line), line))}</td><td><button class="link" data-line="${line.id}">Chain</button></td></tr>`;
  }).join("");
  return `<table><thead><tr><th>Line</th><th>Customer promise</th><th>Date</th><th>Price</th><th>Risk</th><th>Certificate</th><th></th></tr></thead><tbody>${body}</tbody></table>`;
}
document.getElementById("year").innerHTML = [2026,2027,2028,2029,2030].map(year => `<option>${year}</option>`).join("");
document.getElementById("year").onchange = event => { state.year = Number(event.target.value); draw(); };
["decision","customers","chain","agents"].forEach(name => {
  document.getElementById("nav-" + name).onclick = () => { state.page = name; draw(); };
});
draw();
</script>
</body>
</html>
"""


def main() -> None:
    page = HTML.replace("__DATA__", json.dumps(payload()))
    path = ROOT / "index.html"
    path.write_text(page)
    print(path)


if __name__ == "__main__":
    main()
