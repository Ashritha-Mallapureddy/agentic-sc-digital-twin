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
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=Newsreader:opsz,wght@6..72,400;6..72,500&display=swap" rel="stylesheet"/>
<style>
  :root {
    --paper: #f3efe6;
    --ink: #1c1915;
    --muted: #5f584e;
    --line: #ddd4c6;
    --rust: #8c3a2b;
    --pine: #1d5c44;
    --brass: #8a5e2a;
  }
  * { box-sizing: border-box; }
  html { scroll-behavior: smooth; }
  body {
    margin: 0;
    background: var(--paper);
    color: var(--ink);
    font-family: "IBM Plex Sans", "Segoe UI", sans-serif;
    font-size: 15.5px;
    line-height: 1.5;
    font-variant-numeric: tabular-nums;
  }
  .page { max-width: 1040px; margin: 0 auto; padding: 28px 28px 72px; }
  .kicker {
    margin: 0;
    font-size: 11px;
    letter-spacing: .16em;
    text-transform: uppercase;
    color: var(--muted);
    font-weight: 500;
  }
  header { display: flex; justify-content: space-between; gap: 24px; align-items: flex-end; padding-bottom: 18px; border-bottom: 1px solid var(--ink); }
  .brand { font-family: "Newsreader", Georgia, serif; font-size: 28px; font-weight: 500; margin: 4px 0; letter-spacing: -.02em; }
  .quiet { color: var(--muted); }
  .yearbox { text-align: right; }
  select, button, input { font: inherit; color: inherit; }
  select { background: transparent; border: 0; border-bottom: 1px solid var(--ink); padding: 4px 0; }
  section { margin-top: 36px; }
  h2 { font-family: "Newsreader", Georgia, serif; font-weight: 500; font-size: 30px; letter-spacing: -.02em; margin: 0 0 8px; }
  .askbar { display: flex; gap: 12px; align-items: center; border-bottom: 1px solid var(--ink); margin-top: 8px; }
  .askbar input { flex: 1; border: 0; background: transparent; font-family: "Newsreader", Georgia, serif; font-size: 26px; padding: 10px 0; outline: none; }
  .askbar input::placeholder { color: #9a917f; }
  .askbar button, button.record {
    background: var(--ink); color: var(--paper); border: 1px solid var(--ink); padding: 8px 14px; cursor: pointer; letter-spacing: .08em; text-transform: uppercase; font-size: 12px;
  }
  button.record { background: transparent; color: var(--ink); letter-spacing: .04em; text-transform: none; font-size: 14px; margin-top: 14px; }
  button.record:hover, .askbar button:hover { background: var(--ink); color: var(--paper); }
  .tries { margin: 10px 0 0; }
  .tries button { background: transparent; border: 0; border-bottom: 1px solid #cfc6b6; color: var(--muted); padding: 0; margin: 0 16px 6px 0; cursor: pointer; font-size: 13.5px; }
  .tries button:hover { color: var(--ink); border-color: var(--ink); }
  .decision { margin-top: 28px; padding-top: 8px; }
  .decision h1 { font-family: "Newsreader", Georgia, serif; font-weight: 500; font-size: 44px; line-height: 1.08; letter-spacing: -.03em; margin: 8px 0 12px; max-width: 22ch; }
  .sentence, .sequence { max-width: 68ch; margin: 0 0 10px; font-size: 17px; }
  .sequence { color: var(--rust); }
  .facts { display: grid; grid-template-columns: 1.4fr repeat(3, 1fr); gap: 18px; margin: 18px 0 8px; padding: 14px 0; border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); }
  .facts dt { font-size: 11px; letter-spacing: .14em; text-transform: uppercase; color: var(--muted); }
  .facts dd { margin: 4px 0 0; font-size: 18px; }
  .beats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 26px; margin-top: 18px; }
  .beats h3 { margin: 0 0 6px; font-size: 11px; letter-spacing: .14em; text-transform: uppercase; font-weight: 500; color: var(--muted); }
  .beats p { margin: 0; }
  .bridge { margin-top: 8px; }
  .brow { display: grid; grid-template-columns: 260px 1fr 120px; gap: 14px; align-items: center; margin: 9px 0; }
  .track { height: 8px; background: #e6dfd2; }
  .track i { display: block; height: 100%; background: var(--ink); }
  .brow.today .track i { background: var(--rust); }
  .brow.named .track i { background: var(--pine); }
  .brow b { text-align: right; font-weight: 500; }
  .rule { max-width: 78ch; color: var(--muted); margin: 12px 0 0; }
  .legend { color: var(--muted); max-width: 78ch; }
  .swatch { display: inline-block; width: 18px; height: 4px; margin: 0 6px 2px 12px; vertical-align: middle; }
  .listhead { display: flex; justify-content: space-between; gap: 24px; align-items: end; }
  .promise {
    display: grid; grid-template-columns: 88px 1.5fr 132px 128px 92px; gap: 14px; align-items: center;
    width: 100%; text-align: left; background: transparent; border: 0; border-top: 1px solid var(--line);
    padding: 14px 8px; cursor: pointer;
  }
  .promise:hover { background: rgba(28, 25, 21, .03); }
  .promise.on { box-shadow: inset 2px 0 0 var(--rust); }
  .promise strong { font-weight: 500; }
  .pid { font-weight: 500; }
  .meters { display: grid; gap: 4px; }
  .meters i { display: block; height: 4px; }
  .meters i:nth-child(1) { background: var(--ink); }
  .meters i:nth-child(2) { background: var(--rust); }
  .meters i:nth-child(3) { background: var(--pine); }
  .fig { font-weight: 500; }
  .tag { display: block; margin-top: 4px; font-size: 12px; color: var(--muted); }
  .flow { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 22px; margin-top: 16px; }
  .tier h3 { margin: 0 0 8px; font-size: 11px; letter-spacing: .14em; text-transform: uppercase; font-weight: 500; color: var(--muted); }
  .node { border-top: 1px solid var(--line); padding: 12px 0 12px 12px; border-left: 2px solid var(--line); margin-bottom: 8px; }
  .node.verified { border-left-color: var(--pine); }
  .node.named { border-left-color: var(--brass); }
  .node.unknown { border-left-color: var(--rust); border-left-style: dashed; }
  .node .name { margin: 2px 0; font-size: 17px; }
  .node p { margin: 2px 0; }
  .formula { font-size: 15px; padding-top: 8px; }
  .four { display: grid; grid-template-columns: repeat(4, 1fr); gap: 22px; }
  .four div { border-top: 1px solid var(--ink); padding-top: 10px; }
  .four h3 { margin: 0 0 6px; font-size: 16px; font-weight: 500; }
  .four p { margin: 0; }
  footer { margin-top: 48px; padding-top: 16px; border-top: 1px solid var(--line); color: var(--muted); font-size: 13px; }
  button.texty { background: transparent; border: 0; padding: 0; color: var(--ink); cursor: pointer; border-bottom: 1px solid var(--ink); }
  @media (max-width: 860px) {
    .decision h1 { font-size: 34px; }
    .facts, .beats, .four, .flow { grid-template-columns: 1fr; }
    .brow { grid-template-columns: 1fr; gap: 4px; }
    .brow b { text-align: left; }
    .promise { grid-template-columns: 1fr 1fr; }
    header, .listhead { flex-direction: column; align-items: flex-start; }
    .yearbox { text-align: left; }
  }
</style>
</head>
<body>
<div class="page">
  <header>
    <div>
      <p class="kicker">Customer-experience review</p>
      <p class="brand">Agentic CX desk</p>
      <p class="quiet">Linea Automotive GmbH, Düsseldorf · sample declarant · weekly promise review</p>
    </div>
    <div class="yearbox">
      <label class="kicker" for="year">Declaration year</label><br/>
      <select id="year"></select>
    </div>
  </header>
  <main id="main"></main>
</div>
<script>
const DATA = __DATA__;
const INITIAL = DATA.lines.flatMap(line => line.slices.filter(item => item.initial === "verified").map(item => item.id));
const state = { year: 2026, query: "", asked: false, justAsked: false, inspect: null, scrollChain: false,
  verified: new Set(INITIAL) };
const euro = value => "€" + Math.round(value).toLocaleString("en-IE");
const tonnes = value => value.toLocaleString("en-IE");
const markup = (sector, year) => sector === "Fertilisers" ? DATA.fert : DATA.markup[year];
const sliceValue = (item, line) => state.verified.has(item.id) ? item.actual
  : item.default_2026 * (1 + markup(line.sector, state.year)) / (1 + markup(line.sector, 2026));
const intensity = line => line.slices.reduce((sum, item) => sum + sliceValue(item, line), 0);
const marked = line => line.country_default * (1 + markup(line.sector, state.year));
const cost = (embedded, line) => Math.max(0, embedded - DATA.factor[state.year] * line.benchmark) * line.tonnes * DATA.price;
const fullSet = line => new Set(line.slices.map(item => item.id));
const costMode = (line, mode) => {
  const was = state.verified;
  if (mode === "full") state.verified = fullSet(line);
  const value = cost(mode === "default" ? marked(line) : intensity(line), line);
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
  return { delivery: dateOpen ? "Open" : "Held", price: priceOpen ? "Open" : "Firm", complaint, probability, impact, score, band: score >= 15 ? "High" : score >= 8 ? "Medium" : "Low" };
}
function saving(line, item) {
  if (state.verified.has(item.id)) return 0;
  const before = cost(intensity(line), line);
  state.verified.add(item.id);
  const after = cost(intensity(line), line);
  state.verified.delete(item.id);
  return before - after;
}
function actions() {
  const rows = [];
  for (const line of DATA.lines) {
    for (const item of line.slices) {
      const euros = saving(line, item);
      if (euros <= 1) continue;
      rows.push({ ...item, line, euros, verb: item.initial === "unknown" ? "Name the installation and verify it" : "Obtain the verifier's report" });
    }
  }
  rows.sort((a, b) => b.euros - a.euros);
  return rows;
}
const book = mode => DATA.lines.reduce((sum, line) => sum + costMode(line, mode), 0);
const findLine = id => DATA.lines.find(line => line.id === id);
const esc = value => String(value).replace(/[&<>"']/g, mark => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[mark]));
const listNames = items => {
  const names = items.map(item => item.name);
  if (names.length <= 1) return names[0] || "";
  return names.slice(0, -1).join(", ") + " and " + names[names.length - 1];
};
function workshop() {
  const open = DATA.lines.map(line => ({ line, pos: position(line) })).filter(row => row.pos.delivery === "Open" || row.pos.price === "Open");
  if (!open.length) return { choice: null, act: null, aside: null, clear: true };
  open.sort((a, b) => {
    const date = (row) => row.pos.delivery === "Open" ? 1 : 0;
    return date(b) - date(a) || b.pos.score - a.pos.score || b.line.tonnes - a.line.tonnes;
  });
  const choice = open[0].line;
  const act = actions().find(item => item.line.id === choice.id) || null;
  const biggest = actions()[0] || null;
  const aside = biggest && (!act || biggest.id !== act.id) ? biggest : null;
  return { choice, act, aside, clear: false };
}
function matchLine(text) {
  const idHit = text.match(/l-0[1-7]/);
  if (idHit) return findLine(idHit[0].toUpperCase());
  const skip = new Set(["the", "and", "for", "what", "why", "how", "who", "can", "not", "this", "week", "account", "customer", "confirm", "which", "does", "did", "are", "was", "with", "from", "that", "still", "open", "much", "come", "comes", "off", "promise"]);
  const words = text.split(/[^a-z0-9]+/).filter(word => word.length > 2 && !skip.has(word));
  const hits = DATA.lines.filter(line => {
    const hay = [line.id, line.customer, line.good, line.cn, line.origin, line.sector, ...line.slices.map(item => item.name)].join(" ").toLowerCase();
    return words.some(word => hay.includes(word));
  });
  hits.sort((a, b) => position(b).score - position(a).score || b.tonnes - a.tonnes);
  return hits[0] || null;
}
function asideReason(line, aside) {
  const decision = position(line);
  const other = position(aside.line);
  if (decision.delivery === "Open" && other.delivery === "Held") {
    return aside.line.customer + " already has a held date. An open delivery is taken before a larger euro on a held date.";
  }
  if (decision.delivery === "Open" && other.delivery === "Open") {
    return aside.line.customer + " is also an open date, at " + tonnes(aside.line.tonnes) + " tonnes against " + tonnes(line.tonnes) + ". The larger open promise is taken first.";
  }
  return "A larger euro is still in the book. This is the promise the review settles first.";
}
function evidenceText(line) {
  const known = line.slices.filter(item => state.verified.has(item.id));
  const missing = line.slices.filter(item => !state.verified.has(item.id));
  const knownBit = known.length ? "On file: " + listNames(known) + "." : "Nothing on this line is verified.";
  const missBit = missing.length
    ? " Still open: " + missing.map(item => item.name + " (tier " + item.tier + ", " + (item.initial === "unknown" ? "not on the invoice" : "named, no report") + ")").join("; ") + "."
    : " Nothing left open.";
  return knownBit + missBit;
}
function viewLine(line, act, aside) {
  const pos = position(line);
  const missing = line.slices.filter(item => !state.verified.has(item.id));
  const tier1 = missing.filter(item => item.tier === 1);
  const behind = missing.filter(item => item.tier !== 1 && item.initial === "unknown");
  let kicker, sentence;
  if (pos.delivery === "Held" && pos.price === "Firm") {
    kicker = "Release";
    sentence = line.promise + ". The date is held and the quoted price can stand. The certificate on the verified figure is " + euro(cost(intensity(line), line)) + ".";
  } else if (pos.delivery === "Open") {
    kicker = "Hold confirmation";
    const plant = tier1.every(item => item.initial === "unknown")
      ? listNames(tier1) + (tier1.length > 1 ? " are" : " is") + " missing from the invoice, so no delivery date can be held."
      : listNames(tier1) + (tier1.length > 1 ? " are" : " is") + " named on the invoice and not verified, so the delivery date cannot be held.";
    const tail = behind.length ? " " + listNames(behind) + (behind.length > 1 ? " are" : " is") + " not on the invoice." : "";
    sentence = line.promise + ". " + plant + tail;
  } else {
    kicker = "Hold the price";
    sentence = line.promise + ". The plant on the invoice is verified, so the date can stand. The quoted price stays open until these are verified: " + missing.map(item => item.name).join("; ") + ".";
  }
  const now = cost(intensity(line), line);
  const namedCost = costMode(line, "full");
  return {
    kicker, title: line.customer, sentence, lineId: line.id, act,
    sequence: aside ? "The largest gap is " + euro(aside.euros) + " on the " + aside.line.customer + ": " + aside.name + ". " + asideReason(line, aside) : "",
    facts: [
      ["Record", act ? act.name : "Nothing open"],
      ["Comes off", act ? euro(act.euros) : "—"],
      ["Risk", pos.probability + " × " + pos.impact + " = " + pos.score],
      ["Certificate now", euro(now)]
    ],
    beats: [
      ["Promise", line.id + " · " + line.good + ", CN " + line.cn + ". " + line.origin + ". " + tonnes(line.tonnes) + " tonnes. " + line.customer + ": " + line.promise + "."],
      ["Evidence", evidenceText(line)],
      ["Consequence", "Risk " + pos.probability + " × " + pos.impact + " = " + pos.score + ", " + pos.band + ". " + pos.complaint + (act ? " " + act.verb + ": " + act.name + ". " + euro(act.euros) + " comes off the mark-up." : "") + " Today's certificate is " + euro(now) + ". Fully named, it is " + euro(namedCost) + ". That remainder is still paid."]
    ]
  };
}
function viewClear() {
  return {
    kicker: "Release the book", title: "Every promise can stand", lineId: DATA.lines[0].id, act: null, sequence: "",
    sentence: "Every date is held and every quoted price can stand. The certificate on the verified figures is " + euro(book("full")) + ". Nothing left is a mark-up for a missing installation.",
    facts: [["Record", "Nothing open"], ["Comes off", "—"], ["Open promises", "0"], ["Certificate", euro(book("full"))]],
    beats: [
      ["Promise", "Seven accounts, each with a held date and a firm price."],
      ["Evidence", "Every installation in the book has a verifier report, including the sites that were not on the invoice."],
      ["Consequence", "The remaining certificate is the verified embedded emissions."]
    ]
  };
}
function viewSafe() {
  const safe = DATA.lines.filter(line => { const pos = position(line); return pos.price === "Firm" && pos.delivery === "Held"; });
  const weekly = workshop();
  if (!safe.length) {
    const base = viewLine(weekly.choice, weekly.act, weekly.aside);
    base.kicker = "None firm yet";
    base.title = "No account can be released";
    base.sentence = "Every promise still has an open date or an open price. The review takes the open delivery with the most tonnes, then the installation on it that removes the most mark-up.";
    return base;
  }
  return {
    kicker: "Already firm", title: safe.length > 2 ? "Accounts that can stand" : safe.map(line => line.customer).join(" · "),
    lineId: safe[0].id, act: null, sequence: "",
    sentence: safe.map(line => line.id + " " + line.customer + ": date held, price firm, certificate " + euro(cost(intensity(line), line)) + ".").join(" "),
    facts: [["Firm", String(safe.length)], ["Open dates", String(DATA.lines.filter(line => position(line).delivery === "Open").length)], ["Open prices", String(DATA.lines.filter(line => position(line).price === "Open").length)], ["Certificate today", euro(book("today"))]],
    beats: [
      ["Promise", "A firm account is one whose invoice plant and every installation behind it are verified."],
      ["Evidence", safe.map(line => line.id + " " + line.customer).join("; ") + "."],
      ["Consequence", "These quoted prices can stand. The certificate on the verified figure is still paid."]
    ]
  };
}
function viewOutside() {
  const weekly = workshop();
  const base = weekly.clear ? viewClear() : viewLine(weekly.choice, weekly.act, weekly.aside);
  base.kicker = "This book only";
  base.title = "Ask about a promise in the seven lines";
  base.sentence = "Which customer do we hold, why is the coil promise open, what comes off on L-02, or which account is already firm.";
  base.sequence = "";
  return base;
}
function compose(raw) {
  const text = (raw || "").trim().toLowerCase();
  const weekly = workshop();
  if (!text) return weekly.clear ? viewClear() : viewLine(weekly.choice, weekly.act, weekly.aside);
  if (/safe|already firm|already safe|which account is safe|who can we confirm/.test(text)) return viewSafe();
  if (weekly.clear) return viewClear();
  const specific = matchLine(text);
  if (!specific && !/why|missing|because|how much|what do|what should|do we|action|mark-?up|euro|which|who|confirm|risk|promise|certificate|cost|open|largest|biggest|hold/.test(text)) return viewOutside();
  const line = specific || weekly.choice;
  const act = actions().find(item => item.line.id === line.id) || null;
  const aside = !specific && weekly.aside && (!act || weekly.aside.id !== act.id) ? weekly.aside : null;
  return viewLine(line, act, aside);
}
function meter(line) {
  const base = costMode(line, "default");
  const today = cost(intensity(line), line);
  const named = costMode(line, "full");
  const width = value => base > 0 ? Math.max(value > 0 ? 3 : 0, Math.round(value / base * 100)) : 0;
  const tag = Math.abs(today - named) < 1 ? "Fully named" : Math.abs(today - base) < 1 ? "Still the default" : "Part evidenced";
  return `<span><span class="meters" title="Default ${euro(base)}. Today ${euro(today)}. Named ${euro(named)}."><i style="width:${width(base)}%"></i><i style="width:${width(today)}%"></i><i style="width:${width(named)}%"></i></span><span class="tag">${tag}</span></span>`;
}
function ruleText() {
  const steel = Math.round(DATA.markup[state.year] * 100);
  const fert = Math.round(DATA.fert * 100);
  const factor = (DATA.factor[state.year] * 100).toLocaleString("en-IE", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
  return "Certificate price held at €" + DATA.price.toFixed(2) + ". For " + state.year + " the rule is a " + steel + "% mark-up on steel, cement, aluminium and hydrogen, " + fert + "% on fertilisers, and " + factor + "% of the benchmark still covered by free allocation.";
}
function dirty() {
  if (state.verified.size !== INITIAL.length) return true;
  return INITIAL.some(id => !state.verified.has(id));
}
function draw() {
  const spoken = compose(state.asked ? state.query : "");
  const chainLine = findLine(state.inspect || spoken.lineId);
  const today = book("today");
  const full = book("full");
  const base = book("default");
  const scale = base || 1;
  const examples = [
    "Which customer do we hold this week?",
    "Why is that promise still open?",
    "What do we do, and how much comes off?",
    "Which account is already firm?"
  ];
  const bars = [
    ["Country-default path", base, ""],
    ["On today's evidence", today, "today"],
    ["If every installation is named", full, "named"]
  ].map(([label, value, klass]) => `<div class="brow ${klass}"><span>${label}</span><div class="track"><i style="width:${Math.max(2, value / scale * 100)}%"></i></div><b>${euro(value)}</b></div>`).join("");
  const rows = DATA.lines.map(line => {
    const pos = position(line);
    const on = line.id === chainLine.id ? " on" : "";
    return `<button type="button" class="promise${on}" data-line="${line.id}"><span class="pid">${line.id}<span class="tag">${esc(line.good)}</span></span><span><strong>${esc(line.customer)}</strong><span class="tag">${esc(line.promise)}</span></span><span>${pos.delivery} date<span class="tag">${pos.price} price · ${pos.probability} × ${pos.impact} = ${pos.score}</span></span>${meter(line)}<span class="fig">${euro(cost(intensity(line), line))}</span></button>`;
  }).join("");
  const tiers = [1, 2, 3].map(tier => {
    const title = tier === 1 ? "Tier 1 · on the invoice" : tier === 2 ? "Tier 2 · precursors" : "Tier 3 · extraction, often off the invoice";
    const group = chainLine.slices.filter(item => item.tier === tier);
    const cards = group.length ? group.map(item => {
      const known = state.verified.has(item.id);
      const klass = known ? "verified" : item.initial === "unknown" ? "unknown" : "named";
      const label = known ? "Verifier report on file" : item.initial === "unknown" ? "Not on the invoice" : "Named, no verifier report";
      const euros = saving(chainLine, item);
      const money = euros > 1 ? `<p class="quiet">${euro(euros)} comes off if this is recorded</p>` : "";
      const button = known ? "" : `<button type="button" class="record" data-id="${item.id}">Record as verified</button>`;
      return `<div class="node ${klass}"><p class="kicker">${esc(item.role)}</p><p class="name">${esc(item.name)}</p><p class="quiet">${esc(item.place)}</p><p>${sliceValue(item, chainLine).toFixed(3)} tCO2e/t</p><p>${label}</p>${money}${button}</div>`;
    }).join("") : `<div class="node"><p class="quiet">No installation of this tier on the line.</p></div>`;
    return `<div class="tier"><h3>${title}</h3>${cards}</div>`;
  }).join("");
  const embedded = intensity(chainLine);
  const factor = DATA.factor[state.year];
  const formula = "max(0, " + embedded.toFixed(3) + " − " + Number(factor).toFixed(3) + " × " + chainLine.benchmark.toFixed(3) + ") × " + tonnes(chainLine.tonnes) + " t × €" + DATA.price.toFixed(2) + " = " + euro(cost(embedded, chainLine)) + ".";
  const unnamed = DATA.lines.flatMap(line => line.slices).filter(item => item.initial === "unknown" && !state.verified.has(item.id)).length;
  const totalTonnes = DATA.lines.reduce((sum, line) => sum + line.tonnes, 0);
  const weekly = workshop();
  const deskLine = weekly.clear || !weekly.act ? "No mark-up left to remove." : "First record: " + weekly.act.name + ", " + euro(weekly.act.euros) + ", on " + weekly.choice.customer + ".";
  const facts = spoken.facts.map(([dt, dd]) => `<div><dt>${esc(dt)}</dt><dd>${esc(dd)}</dd></div>`).join("");
  const beats = spoken.beats.map(([title, text]) => `<div><h3>${esc(title)}</h3><p>${esc(text)}</p></div>`).join("");
  const sequence = spoken.sequence ? `<p class="sequence">${esc(spoken.sequence)}</p>` : "";
  const record = spoken.act ? `<button type="button" class="record" id="do-top">Record ${esc(spoken.act.name)} as verified</button>` : "";
  const inspectNote = state.inspect && state.inspect !== spoken.lineId ? `<p class="quiet">Opened from the list. The judgment above stays on ${esc(findLine(spoken.lineId).customer)}.</p>` : "";
  document.getElementById("main").innerHTML = `
    <section class="ask">
      <p class="kicker">Ask the review</p>
      <form id="ask" class="askbar">
        <input id="q" type="text" placeholder="Ask about a promise, a missing installation, or the euro" value="${esc(state.query)}" autocomplete="off"/>
        <button type="submit">Ask</button>
      </form>
      <p class="tries">${examples.map(text => `<button type="button" data-try="${esc(text)}">${esc(text)}</button>`).join("")}</p>
    </section>
    <section class="decision">
      <p class="kicker">${esc(spoken.kicker)}</p>
      <h1>${esc(spoken.title)}</h1>
      <p class="sentence">${esc(spoken.sentence)}</p>
      ${sequence}
      <dl class="facts">${facts}</dl>
      ${record}
      <div class="beats">${beats}</div>
    </section>
    <section>
      <h2>What the workshop can still move</h2>
      <p class="legend">The gap between today's evidence and a fully named book is the mark-up. The named figure remains payable.</p>
      <div class="bridge">${bars}</div>
      <p class="rule">${esc(ruleText())} Mark-up still in the book: ${euro(today - full)}.</p>
    </section>
    <section>
      <div class="listhead">
        <h2>Seven promises</h2>
        <p class="legend"><i class="swatch" style="background:#1c1915"></i>country default <i class="swatch" style="background:#8c3a2b"></i>today <i class="swatch" style="background:#1d5c44"></i>if named</p>
      </div>
      <p class="legend">Date open is a delivery risk, Liefertreue. Price open is an order change or a surcharge complaint, Auftragsänderung and Reklamation. Risk is probability × impact. Where the first two marks are the same length, the line is still entirely on the country default.</p>
      <div>${rows}</div>
    </section>
    <section id="chain">
      <h2>Behind the invoice · ${esc(chainLine.id)} ${esc(chainLine.good)}</h2>
      <p class="legend">${esc(chainLine.customer)}. ${esc(chainLine.origin)}. The invoice names tier 1. The certificate also depends on the coke, the coal, the ore or the gas behind that plant.</p>
      ${inspectNote}
      <div class="flow">${tiers}</div>
      <p class="formula">${esc(formula)}</p>
      <p class="quiet">${esc(chainLine.default_note)} ${esc(chainLine.benchmark_note || "")}</p>
    </section>
    <section>
      <h2>How the review is split</h2>
      <div class="four">
        <div><h3>Customs reader</h3><p>${DATA.lines.length} lines, ${tonnes(totalTonnes)} tonnes. Above the 50-tonne threshold, so an authorised declarant files the book.</p></div>
        <div><h3>Chain scout</h3><p>${unnamed} installations are still unnamed behind the invoice, including coal, ore, gas and the mine the importer does not contract.</p></div>
        <div><h3>Emissions clerk</h3><p>Today's book is ${euro(today)}. ${euro(today - full)} of that exists because a slice still uses the marked country default.</p></div>
        <div><h3>Certificate desk</h3><p>${esc(deskLine)} The certificate on a verified figure is still paid.</p></div>
      </div>
    </section>
    <footer>
      <p>Installation names and their actual figures are synthetic. Country defaults, the mark-up schedule, the CBAM factor and the Q3 2026 certificate price of €82.32 follow the published method. A filing uses the Commission Excel. Carbon price already paid is zero in this book. Owner of the open item: the CX PMO analyst.</p>
      ${dirty() ? `<p><button type="button" class="texty" id="reset">Return to the evidence the book started with</button></p>` : ""}
    </footer>`;
  document.getElementById("ask").onsubmit = event => {
    event.preventDefault();
    state.query = document.getElementById("q").value;
    state.asked = true;
    state.justAsked = true;
    state.inspect = null;
    draw();
  };
  document.querySelectorAll("[data-try]").forEach(button => button.onclick = () => {
    state.query = button.dataset.try;
    state.asked = true;
    state.justAsked = true;
    state.inspect = null;
    draw();
  });
  const go = document.getElementById("do-top");
  if (go && spoken.act) go.onclick = () => { state.verified.add(spoken.act.id); state.inspect = null; draw(); };
  document.querySelectorAll("button.promise").forEach(button => button.onclick = () => {
    state.inspect = button.dataset.line;
    state.scrollChain = true;
    draw();
  });
  document.querySelectorAll("button.record[data-id]").forEach(button => button.onclick = () => {
    state.verified.add(button.dataset.id);
    draw();
  });
  const reset = document.getElementById("reset");
  if (reset) reset.onclick = () => { state.verified = new Set(INITIAL); state.inspect = null; draw(); };
  const box = document.getElementById("q");
  if (state.justAsked && box) { box.focus({ preventScroll: true }); state.justAsked = false; }
  if (state.scrollChain) {
    document.getElementById("chain").scrollIntoView({ behavior: "smooth", block: "start" });
    state.scrollChain = false;
  }
}
document.getElementById("year").innerHTML = [2026, 2027, 2028, 2029, 2030].map(year => `<option>${year}</option>`).join("");
document.getElementById("year").onchange = event => { state.year = Number(event.target.value); draw(); };
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
