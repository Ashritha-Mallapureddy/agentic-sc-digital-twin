"""Small agentic digital twin for a fictional adhesives network.

One shared state. Inventory releases supply. Outbound stock is split by need.
The mode picks the lane. The twin is a teaching model: mass balance and a
forecast. It is not a trained language model and it does not reproduce the
papers it cites.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "output"

REGIONS = ("DE", "FR", "NL", "PL")
BASE_DEMAND = {"DE": 220.0, "FR": 120.0, "NL": 80.0, "PL": 70.0}
WEEKS = 16

MODES = ("service", "balanced", "low_carbon")


@dataclass
class Action:
    agent: str
    name: str
    rationale: str
    kind: str
    qty: float
    region: str | None
    lead: int
    cost: float
    co2: float


def initial_state() -> dict:
    return {
        "resin": 700.0,
        "pack": 280.0,
        "fg_plant": 180.0,
        "fg_dc": 420.0,
        "backlog": {region: 0.0 for region in REGIONS},
        "level": dict(BASE_DEMAND),
        "pipeline": [
            {"kind": "resin", "qty": 620.0, "arrives_in": 1, "region": None},
            {"kind": "pack", "qty": 170.0, "arrives_in": 1, "region": None},
            {"kind": "fg_dc", "qty": 360.0, "arrives_in": 1, "region": None},
            {"kind": "customer", "qty": 200.0, "arrives_in": 1, "region": "DE"},
            {"kind": "customer", "qty": 90.0, "arrives_in": 1, "region": "FR"},
        ],
        "fulfilled": 0.0,
        "demand_total": 0.0,
        "cost": 0.0,
        "co2": 0.0,
        "expedite_qty": 0.0,
        "rail_qty": 0.0,
        "truck_qty": 0.0,
    }


def demand_for(week: int, scenario: str) -> dict[str, float]:
    # Deterministic swing so two runs of the same scenario match.
    swing = 1 + 0.04 * ((week % 5) - 2) / 2
    demand = {region: round(base * swing, 1) for region, base in BASE_DEMAND.items()}
    if scenario == "demand_spike" and 6 <= week <= 9:
        demand["DE"] = round(demand["DE"] * 1.40, 1)
        demand["FR"] = round(demand["FR"] * 1.30, 1)
    return demand


def constraints(week: int, scenario: str) -> tuple[float, int]:
    resin_cap = 650.0
    resin_lead = 1
    if scenario == "resin_short" and 8 <= week <= 11:
        resin_cap = 150.0
    if scenario == "port_delay" and 5 <= week <= 12:
        resin_lead = 3
    return resin_cap, resin_lead


def land(state: dict, arrived: list[dict]) -> dict[str, float]:
    at_customer = {region: 0.0 for region in REGIONS}
    for shipment in arrived:
        if shipment["kind"] == "resin":
            state["resin"] += shipment["qty"]
        elif shipment["kind"] == "pack":
            state["pack"] += shipment["qty"]
        elif shipment["kind"] == "fg_dc":
            state["fg_dc"] += shipment["qty"]
        elif shipment["kind"] == "customer":
            at_customer[shipment["region"]] += shipment["qty"]
    return at_customer


def propose(state: dict, forecast: dict[str, float], week: int, scenario: str) -> list[Action]:
    resin_cap, resin_lead = constraints(week, scenario)
    actions: list[Action] = []
    forecast_total = sum(forecast.values())
    backlog_total = sum(state["backlog"].values())
    producible = min(560.0, state["resin"], state["pack"] / 0.25, forecast_total + 0.25 * backlog_total)
    if producible >= 20:
        actions.append(
            Action(
                "inventory",
                "Produce to the forecast",
                f"Plant can finish {producible:.0f} kits from resin and packaging already on hand.",
                "produce",
                round(producible, 1),
                None,
                0,
                round(producible * 0.80, 1),
                round(producible * 0.03, 2),
            )
        )
    upcoming = producible if producible >= 20 else 0.0
    transfer_qty = max(0.0, state["fg_plant"] + upcoming - 80.0)
    if transfer_qty >= 20:
        actions.append(
            Action(
                "inventory",
                "Move finished goods to Duisburg",
                f"Keep 80 kits at the plant for a same-week expedite. Send {transfer_qty:.0f} to the DC.",
                "to_dc",
                round(transfer_qty, 1),
                None,
                0,
                round(transfer_qty * 0.50, 1),
                round(transfer_qty * 0.05, 2),
            )
        )
    resin_transit = sum(item["qty"] for item in state["pipeline"] if item["kind"] == "resin")
    cover_weeks = resin_lead + 1
    resin_gap = cover_weeks * max(forecast_total, 1) - (state["resin"] + resin_transit)
    resin_qty = min(resin_cap, max(0.0, resin_gap))
    if resin_qty >= 40:
        actions.append(
            Action(
                "inventory",
                "Replenish resin",
                f"Resin position is short of {cover_weeks:.0f} weeks (lead time plus one). Supplier can release {resin_qty:.0f}.",
                "resin",
                round(resin_qty, 1),
                None,
                resin_lead,
                round(resin_qty * 2.20, 1),
                round(resin_qty * 0.11, 2),
            )
        )
    pack_transit = sum(item["qty"] for item in state["pipeline"] if item["kind"] == "pack")
    pack_gap = 0.25 * 2 * max(forecast_total, 1) - (state["pack"] + pack_transit)
    pack_qty = min(250.0, max(0.0, pack_gap))
    if pack_qty >= 15:
        actions.append(
            Action(
                "inventory",
                "Replenish packaging",
                f"Packaging cover is short. Order {pack_qty:.0f}.",
                "pack",
                round(pack_qty, 1),
                None,
                1,
                round(pack_qty * 0.60, 1),
                round(pack_qty * 0.04, 2),
            )
        )

    return actions


def customer_actions(state: dict, forecast: dict[str, float], mode: str) -> list[Action]:
    """Fair-share outbound. One mode per region, so a large backlog cannot take the whole DC."""
    needs = {region: state["backlog"][region] + forecast[region] for region in REGIONS}
    total_need = sum(needs.values())
    actions: list[Action] = []
    if total_need > 0 and state["fg_dc"] >= 10:
        for region in REGIONS:
            qty = min(needs[region], state["fg_dc"] * needs[region] / total_need)
            if qty < 8:
                continue
            truck_lead = 0 if region == "DE" else 1
            use_rail = mode == "low_carbon" or (mode == "balanced" and state["backlog"][region] <= 1)
            if use_rail:
                actions.append(
                    Action(
                        "sustainability" if mode == "low_carbon" else "service",
                        f"Rail to {region}",
                        f"Fair share for {region} goes by rail. The extra week is the cost of the {mode} mode.",
                        "rail",
                        round(qty, 1),
                        region,
                        truck_lead + 1,
                        round(qty * 1.05, 1),
                        round(qty * 0.04, 2),
                    )
                )
            else:
                actions.append(
                    Action(
                        "service",
                        f"Truck to {region}",
                        f"Fair share for {region} leaves Duisburg on the truck lane.",
                        "truck",
                        round(qty, 1),
                        region,
                        truck_lead,
                        round(qty * (1.10 if region == "DE" else 1.70), 1),
                        round(qty * (0.16 if region == "DE" else 0.28), 2),
                    )
                )
    backlog_total = sum(state["backlog"].values())
    if mode == "service" and backlog_total > 40 and state["fg_plant"] >= 20:
        worst = max(REGIONS, key=lambda region: state["backlog"][region])
        qty = min(80.0, state["fg_plant"], state["backlog"][worst])
        if qty >= 15:
            actions.append(
                Action(
                    "service",
                    f"Expedite to {worst}",
                    f"{worst} holds the largest backlog. Expedite spends the plant buffer, not the DC fair share.",
                    "expedite",
                    round(qty, 1),
                    worst,
                    0,
                    round(qty * 4.80, 1),
                    round(qty * 0.55, 2),
                )
            )
    return actions


def apply_action(state: dict, action: Action, at_customer: dict[str, float]) -> None:
    state["cost"] += action.cost
    state["co2"] += action.co2
    if action.kind == "produce":
        made = min(action.qty, state["resin"], state["pack"] / 0.25)
        state["resin"] -= made
        state["pack"] -= made * 0.25
        state["fg_plant"] += made
        action.qty = round(made, 1)
    elif action.kind == "to_dc":
        moved = min(action.qty, state["fg_plant"])
        state["fg_plant"] -= moved
        state["fg_dc"] += moved
        action.qty = round(moved, 1)
    elif action.kind == "resin":
        state["pipeline"].append({"kind": "resin", "qty": action.qty, "arrives_in": action.lead, "region": None})
    elif action.kind == "pack":
        state["pipeline"].append({"kind": "pack", "qty": action.qty, "arrives_in": action.lead, "region": None})
    elif action.kind == "expedite":
        moved = min(action.qty, state["fg_plant"])
        state["fg_plant"] -= moved
        at_customer[action.region] += moved
        state["expedite_qty"] += moved
        action.qty = round(moved, 1)
    elif action.kind in {"truck", "rail"}:
        moved = min(action.qty, state["fg_dc"])
        state["fg_dc"] -= moved
        if action.kind == "rail":
            state["rail_qty"] += moved
        else:
            state["truck_qty"] += moved
        if action.lead <= 0:
            at_customer[action.region] += moved
        else:
            state["pipeline"].append(
                {"kind": "customer", "qty": moved, "arrives_in": action.lead, "region": action.region}
            )
        action.qty = round(moved, 1)


def fulfill(state: dict, demand: dict[str, float], at_customer: dict[str, float]) -> dict[str, float]:
    served = {}
    for region in REGIONS:
        need = state["backlog"][region] + demand[region]
        got = min(need, at_customer[region])
        state["backlog"][region] = round(need - got, 1)
        served[region] = round(got, 1)
        state["fulfilled"] += got
        state["demand_total"] += demand[region]
    return served


def simulate(scenario: str, mode: str) -> dict:
    state = initial_state()
    weeks = []
    for week in range(1, WEEKS + 1):
        arrived = []
        still = []
        for shipment in state["pipeline"]:
            shipment["arrives_in"] -= 1
            if shipment["arrives_in"] <= 0:
                arrived.append(shipment)
            else:
                still.append(shipment)
        state["pipeline"] = still
        at_customer = land(state, arrived)
        demand = demand_for(week, scenario)
        forecast = dict(state["level"])
        structural = propose(state, forecast, week, scenario)
        structural.sort(key=lambda action: {"produce": 0, "to_dc": 1, "resin": 2, "pack": 3}[action.kind])
        for action in structural:
            apply_action(state, action, at_customer)
        outbound = customer_actions(state, forecast, mode)
        for action in outbound:
            apply_action(state, action, at_customer)
        chosen = [action for action in structural + outbound if action.qty > 0]
        served = fulfill(state, demand, at_customer)
        for region in REGIONS:
            state["level"][region] = round(0.45 * demand[region] + 0.55 * state["level"][region], 1)
        backlog = round(sum(state["backlog"].values()), 1)
        weeks.append(
            {
                "week": week,
                "demand": round(sum(demand.values()), 1),
                "served": round(sum(served.values()), 1),
                "backlog": backlog,
                "fill_rate": round(state["fulfilled"] / state["demand_total"], 3),
                "resin": round(state["resin"], 1),
                "fg_dc": round(state["fg_dc"], 1),
                "fg_plant": round(state["fg_plant"], 1),
                "cost": round(state["cost"], 1),
                "co2": round(state["co2"], 1),
                "actions": [
                    {
                        "agent": action.agent,
                        "name": action.name,
                        "qty": action.qty,
                        "rationale": action.rationale,
                        "cost": action.cost,
                        "co2": action.co2,
                    }
                    for action in chosen
                    if action.qty > 0
                ],
            }
        )
    outbound = state["truck_qty"] + state["rail_qty"] + state["expedite_qty"]
    return {
        "scenario": scenario,
        "mode": mode,
        "fill_rate": round(state["fulfilled"] / state["demand_total"], 3),
        "ending_backlog": round(sum(state["backlog"].values()), 1),
        "cost": round(state["cost"], 1),
        "co2": round(state["co2"], 1),
        "expedite_qty": round(state["expedite_qty"], 1),
        "rail_share": round(state["rail_qty"] / outbound, 3) if outbound else 0,
        "weeks": weeks,
    }


def run_all() -> list[dict]:
    results = []
    for scenario in ("baseline", "resin_short", "port_delay", "demand_spike"):
        for mode in MODES:
            results.append(simulate(scenario, mode))
    return results


def write_outputs(results: list[dict]) -> None:
    DATA.mkdir(exist_ok=True)
    OUT.mkdir(exist_ok=True)
    (DATA / "scenario_results.json").write_text(json.dumps(results, indent=2))
    by_key = {(item["scenario"], item["mode"]): item for item in results}
    lines = [
        "# Decision memo · agentic twin",
        "",
        "RheinAdhesives network, synthetic. Sixteen weeks. Supplier resin, supplier packaging, Cologne plant, Duisburg DC, customers in DE, FR, NL, and PL.",
        "",
        "This memo is the orchestrator's output. It is not a forecast of a real company and it does not use employer data.",
        "",
        "## Recommendation",
        "",
    ]
    base_service = by_key[("baseline", "service")]
    base_carbon = by_key[("baseline", "low_carbon")]
    short_balanced = by_key[("resin_short", "balanced")]
    short_service = by_key[("resin_short", "service")]
    lines.append(
        f"On the undisturbed network, low-carbon mode finishes at fill rate {base_carbon['fill_rate']:.1%} "
        f"and {base_carbon['co2']:.0f} CO₂ units, against service mode at {base_service['fill_rate']:.1%} "
        f"and {base_service['co2']:.0f}. Rail share is {base_carbon['rail_share']:.0%} in low-carbon mode "
        f"and {base_service['rail_share']:.0%} in service mode."
    )
    lines.append("")
    lines.append(
        f"A four-week resin shortage is not a mode problem. Balanced mode ends at fill rate {short_balanced['fill_rate']:.1%} "
        f"with backlog {short_balanced['ending_backlog']:.0f}. Service mode, which may expedite, ends at "
        f"{short_service['fill_rate']:.1%} with backlog {short_service['ending_backlog']:.0f}. "
        "Expediting moves finished goods that already exist. It does not create resin."
    )
    lines.append("")
    lines.append(
        "Keep the low-carbon lane while backlog is only the rail delay itself. When a resin constraint is open, switch the mode to service: the truck lane and the plant buffer recover units that already exist. Switch back once the constraint has passed. Do not leave the premium lane on as a habit."
    )
    lines.append("")
    lines.append("## Scenario table")
    lines.append("")
    lines.append("| Scenario | Mode | Fill rate | Ending backlog | Cost | CO₂ | Rail share | Expedite qty |")
    lines.append("| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |")
    for item in results:
        lines.append(
            f"| {item['scenario']} | {item['mode']} | {item['fill_rate']:.1%} | {item['ending_backlog']:.0f} | {item['cost']:.0f} | {item['co2']:.0f} | {item['rail_share']:.0%} | {item['expedite_qty']:.0f} |"
        )
    lines.append("")
    lines.append("## What each agent is allowed to do")
    lines.append("")
    lines.append("- Inventory releases production, the Duisburg shuttle, and replenishment. Resin cover is lead time plus one week, capped by what the supplier will release.")
    lines.append("- Outbound stock is split in proportion to each region's backlog plus forecast.")
    lines.append("- Service mode sends that share by truck and may expedite up to 80 kits from the plant buffer.")
    lines.append("- Balanced mode uses rail only for a region whose backlog is already cleared. Low-carbon mode uses rail for every share.")
    lines.append("- Disruption is not a suggestion. It changes resin capacity or resin lead time for the weeks of the scenario.")
    lines.append("")
    lines.append("CO₂ and cost units are model units, comparable inside this twin and not convertible to a published corporate footprint.")
    (OUT / "decision_memo.md").write_text("\n".join(lines) + "\n")


def main() -> None:
    results = run_all()
    write_outputs(results)
    print(f"Wrote {DATA / 'scenario_results.json'}")


if __name__ == "__main__":
    main()
