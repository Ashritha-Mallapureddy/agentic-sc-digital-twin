# Agentic digital twin for a supply chain

**Open the decision memo:** [ashritha-mallapureddy.github.io/agentic-sc-digital-twin](https://ashritha-mallapureddy.github.io/agentic-sc-digital-twin/)

SRH-style project, 2026. A small decision-support twin for a fictional adhesives network: resin supplier, packaging supplier, a plant in Cologne, a DC in Duisburg, and customers in Germany, France, the Netherlands, and Poland.

The twin is agentic in a narrow, inspectable sense. Each week, inventory reads one shared state and releases production, a plant-to-DC shuttle, and replenishment inside capacity. Customer stock at the DC is then split across regions in proportion to backlog plus forecast, so one late region cannot take the whole warehouse. The mode chooses the lane: service uses truck and may expedite from a plant buffer, balanced uses rail only after a region's backlog is cleared, low-carbon puts every fair share on rail. There is no external AI API. The forecast is exponential smoothing. The physics are a mass balance.

## Scenarios

| Scenario | What is disturbed |
| --- | --- |
| baseline | Seasonal swing only |
| resin_short | Resin releases fall to 260 kits in weeks 8–10 |
| port_delay | Resin lead time becomes 3 weeks in weeks 5–12 |
| demand_spike | Germany and France demand jumps in weeks 6–9 |

Modes are weights, not different supply chains: `service`, `balanced`, `low_carbon`.

## What to open

| Artifact | Why it exists |
| --- | --- |
| `output/decision_memo.md` | The recommendation and the full scenario table. |
| `src/twin.py` | State, agents, orchestrator, weekly clock. |
| `docs/literature.md` | Which papers informed the design, and what was not copied. |
| `app.py` | Fill rate, backlog, and the action log for one scenario. |

## Run

```bash
cd agentic-sc-digital-twin
python src/twin.py
python -m streamlit run app.py
```

Results are deterministic. CO₂ and cost are model units for comparison inside this network.

## How to talk about it

Start with the shortage. Expediting raises cost and CO₂ and still cannot create resin. Then show the baseline comparison: low-carbon weights move volume to rail when backlog is zero, and the memo states the fill-rate consequence instead of hiding it. Then open one week in the action log and read the rationale. If you cannot explain a committed row from the stock position, the row should not be in the demo.
