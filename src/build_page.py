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
  .askbar { display:flex; gap:8px; background:white; border:2px solid var(--navy); padding:8px; }
  .askbar input { flex:1; border:0; font:inherit; font-size:16px; padding:8px; outline:none; }
  .askbar button { background:var(--navy); color:white; border:0; padding:8px 18px; cursor:pointer; }
  .tries { margin:8px 0 0; }
  .tries button { background:transparent; border:0; color:var(--navy); cursor:pointer; text-decoration:underline; padding:0 10px 0 0; font:inherit; font-size:13px; }
  .answer { font-size:22px; font-weight:650; letter-spacing:-.02em; margin:6px 0 8px; }
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
  query: "",
  asked: false,
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
const esc = value => String(value).replace(/[&<>"']/g, mark => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[mark]));
function reply(raw) {
  const text = (raw || "").trim().toLowerCase();
  const ranked = DATA.lines.map(line => ({ line, pos: position(line) })).sort((a, b) => b.pos.score - a.pos.score || b.line.tonnes - a.line.tonnes);
  const top = ranked[0];
  const skip = new Set(["the", "and", "for", "what", "why", "how", "who", "can", "not", "this", "week", "account", "customer", "confirm", "which", "does", "did", "are", "was", "with", "from", "that", "still", "open", "much", "come", "comes", "off"]);
  const words = text.split(/[^a-z0-9]+/).filter(word => word.length > 2 && !skip.has(word));
  const hits = DATA.lines.filter(line => {
    const hay = [line.id, line.customer, line.good, line.cn, line.origin, line.sector, ...line.slices.map(item => item.name)].join(" ").toLowerCase();
    return words.some(word => hay.includes(word));
  });
  const line = (hits.sort((a, b) => position(b).score - position(a).score)[0]) || top.line;
  const pos = position(line);
  const act = actions().find(item => item.line.id === line.id);
  const missing = line.slices.filter(item => !state.verified.has(item.id));
  const safe = DATA.lines.filter(item => position(item).price === "Firm" && position(item).delivery === "Held");
  if (!text) return { answer: "Type a question in the bar, then press Ask.", act: null };
  if (/safe|already firm|already safe|who can we confirm|which account is safe/.test(text)) {
    return { answer: safe.length ? safe.map(item => `${item.id} ${item.customer}: date held, price firm, certificate ${euro(cost(intensity(item), item))}.`).join(" ") : "None. Every account still has an open date or an open price.", act: null };
  }
  if (/why|missing|because|behind|reason/.test(text)) {
    return { answer: missing.length ? `${line.customer} was promised: ${line.promise} Still missing: ${missing.map(item => item.name).join("; ")}. ${pos.complaint}` : `${line.customer} has no missing installation. The date is ${pos.delivery} and the price is ${pos.price}.`, act };
  }
  if (/how much|what do|what should|do we|action|mark-?up|euro|remove|owner|next step/.test(text)) {
    return { answer: act ? `${act.verb}: ${act.name}. That removes ${euro(act.euros)} of mark-up on ${line.id}, ${line.customer}. Owner: the CX PMO analyst. The certificate on the verified figure is still paid.` : `Nothing to remove on ${line.customer}. The remaining certificate is the verified figure.`, act };
  }
  if (/certificate|cost|bill|how many euro|€/.test(text) && !/mark-?up/.test(text)) {
    return { answer: hits.length ? `${line.id} ${line.customer}: certificate ${euro(cost(intensity(line), line))} on today's evidence. Country default would be ${euro(costMode(line, "default"))}.` : `The book is ${euro(book("today"))} on today's evidence. The mark-up still in it is ${euro(book("today") - book("full"))}.`, act: null };
  }
  if (/which|who|not confirm|do not confirm|don't confirm|refuse|priority|risk|promise/.test(text) || hits.length) {
    if (hits.length && !/which customer|who do we|not confirm|do not confirm|don't confirm|refuse/.test(text)) {
      return { answer: `${line.id} ${line.customer}. Date ${pos.delivery}. Price ${pos.price}. Risk ${pos.score}, ${pos.band}. ${pos.complaint}`, act };
    }
    return { answer: top.pos.score <= 2 ? "Confirm the book. Every customer promise has a held date and a firm price." : `Do not confirm ${top.line.customer} (${top.line.id}). The date is ${top.pos.delivery}. The price is ${top.pos.price}. Risk ${top.pos.score}, ${top.pos.band}.`, act: actions().find(item => item.line.id === top.line.id) };
  }
  return { answer: "Ask about this book. For example: which customer do we not confirm, why is the coil promise open, what do we do on L-02, how much comes off, or which account is safe.", act: null };
}
function draw() {
  document.querySelectorAll("nav button").forEach(button => button.classList.toggle("on", button.id === "nav-" + state.page));
  const openPrice = DATA.lines.filter(line => position(line).price === "Open").length;
  const openDate = DATA.lines.filter(line => position(line).delivery === "Open").length;
  const today = book("today");
  const full = book("full");
  const main = document.getElementById("main");
  if (state.page === "decision") {
    const spoken = state.asked ? reply(state.query) : { answer: "The answer appears here after you press Ask.", act: null };
    const examples = [
      "Which customer do we not confirm this week?",
      "Why is that promise still open?",
      "What do we do, and how much comes off?",
      "Which account is already safe?"
    ];
    main.innerHTML = `
      <h2>Ask the desk</h2>
      <form id="ask" class="askbar">
        <input id="q" type="text" placeholder="Type a question, then press Ask" value="${esc(state.query)}" autocomplete="off"/>
        <button type="submit">Ask</button>
      </form>
      <p class="tries note">Try ${examples.map(text => `<button type="button" data-try="${esc(text)}">${esc(text)}</button>`).join("")}</p>
      <div class="card high">
        <span class="note">Answer</span>
        <p class="answer">${esc(spoken.answer)}</p>
        ${spoken.act ? `<button class="go" id="do-top">Record ${esc(spoken.act.name)} as verified</button>` : ""}
      </div>
      <div class="kpis">
        <div class="kpi"><span>Open price · order change</span><b>${openPrice} of ${DATA.lines.length}</b></div>
        <div class="kpi"><span>Open date · delivery</span><b>${openDate} of ${DATA.lines.length}</b></div>
        <div class="kpi"><span>Mark-up still in the book</span><b>${euro(today - full)}</b></div>
        <div class="kpi"><span>Certificate on today's evidence</span><b>${euro(today)}</b></div>
      </div>
      ${table()}`;
    document.getElementById("ask").onsubmit = event => {
      event.preventDefault();
      state.query = document.getElementById("q").value;
      state.asked = true;
      draw();
    };
    main.querySelectorAll("[data-try]").forEach(button => button.onclick = () => {
      state.query = button.dataset.try;
      state.asked = true;
      draw();
    });
    const go = document.getElementById("do-top");
    if (go && spoken.act) go.onclick = () => { state.verified.add(spoken.act.id); draw(); };
    const box = document.getElementById("q");
    if (box) box.focus();
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
