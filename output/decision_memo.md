# Decision memo · agentic twin

RheinAdhesives network, synthetic. Sixteen weeks. Supplier resin, supplier packaging, Cologne plant, Duisburg DC, customers in DE, FR, NL, and PL.

This memo is the orchestrator's output. It is not a forecast of a real company and it does not use employer data.

## Recommendation

On the undisturbed network, low-carbon mode finishes at fill rate 98.8% and 1817 CO₂ units, against service mode at 100.0% and 3415. Rail share is 100% in low-carbon mode and 0% in service mode.

A four-week resin shortage is not a mode problem. Balanced mode ends at fill rate 82.2% with backlog 1391. Service mode, which may expedite, ends at 89.7% with backlog 808. Expediting moves finished goods that already exist. It does not create resin.

Keep the low-carbon lane while backlog is only the rail delay itself. When a resin constraint is open, switch the mode to service: the truck lane and the plant buffer recover units that already exist. Switch back once the constraint has passed. Do not leave the premium lane on as a habit.

## Scenario table

| Scenario | Mode | Fill rate | Ending backlog | Cost | CO₂ | Rail share | Expedite qty |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | service | 100.0% | 0 | 39034 | 3415 | 0% | 147 |
| baseline | balanced | 98.9% | 87 | 38678 | 3180 | 18% | 0 |
| baseline | low_carbon | 98.8% | 92 | 35787 | 1817 | 100% | 0 |
| resin_short | service | 89.7% | 808 | 34358 | 3081 | 0% | 627 |
| resin_short | balanced | 82.2% | 1391 | 32071 | 2619 | 21% | 0 |
| resin_short | low_carbon | 81.1% | 1482 | 29526 | 1497 | 100% | 0 |
| port_delay | service | 94.0% | 467 | 36802 | 3302 | 0% | 867 |
| port_delay | balanced | 87.7% | 959 | 33756 | 2829 | 16% | 0 |
| port_delay | low_carbon | 85.9% | 1102 | 31103 | 1578 | 100% | 0 |
| demand_spike | service | 100.0% | 0 | 41806 | 3677 | 0% | 329 |
| demand_spike | balanced | 98.3% | 140 | 40476 | 3324 | 17% | 0 |
| demand_spike | low_carbon | 97.6% | 199 | 37541 | 1906 | 100% | 0 |

## What each agent is allowed to do

- Inventory releases production, the Duisburg shuttle, and replenishment. Resin cover is lead time plus one week, capped by what the supplier will release.
- Outbound stock is split in proportion to each region's backlog plus forecast.
- Service mode sends that share by truck and may expedite up to 80 kits from the plant buffer.
- Balanced mode uses rail only for a region whose backlog is already cleared. Low-carbon mode uses rail for every share.
- Disruption is not a suggestion. It changes resin capacity or resin lead time for the weeks of the scenario.

CO₂ and cost units are model units, comparable inside this twin and not convertible to a published corporate footprint.
