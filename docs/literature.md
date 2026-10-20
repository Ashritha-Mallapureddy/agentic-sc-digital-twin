# What this twin takes from the reading

The model is original coursework-style code. It does not copy the papers and it does not reimplement their empirical studies. The reading is used as a design checklist.

| Reading | What was taken |
| --- | --- |
| Ivanov, D. (2026). Agentic digital twins: bridging model-based and AI-driven decision-making support. *International Journal of Production Research*. https://doi.org/10.1080/00207543.2026.2630277 | The idea that a supply-chain twin is more than a dashboard: model-based rules and software agents share one state. ICARUS (Interaction, Creativity, Adaptation, Reasoning, Ubiquity, Synchronization) is used below as headings for this code, not as a summary of the paper. |
| Abdallah-Ou-Moussa, S., Wynn, M., and Rouaine, Z. (2026). Leveraging blockchain and digital twins for low-carbon, circular supply chains. *Sustainability, 18*, 991. | Service level is not the only objective. The orchestrator can be weighted toward CO₂, and the memo shows what that costs in fill rate. Traceability of the decision sits in the action log rather than in a blockchain. |
| Chouhan and Sahu (2026). Optimizing sustainability in food supply chains through strategic digital twins enablers: a gray influence analysis (GINA). *NMIMS Management Review, 34*(1), 19–38. https://doi.org/10.1177/09711023251400099 | Their enabler ranking puts visibility and collaboration first. In this twin, visibility is the shared state (on-hand, pipeline, backlog). Collaboration is the rule that rail is only offered when customer backlog is already zero, so sustainability does not silently take service from the customer. |
| Bean, T., Monfared, R., Segura-Velandia, D., and Fuller, L. *Journal of Intelligent Manufacturing*. https://doi.org/10.1007/s10845-025-02727-w | A twin on top of a messy operation needs a business test, not a technology tour. The test here is the scenario table: fill rate, backlog, cost, CO₂. |
| Rabadi, G., and Soykan, B. (eds.). *Optimizing Supply Chains Through Digital Twins*. Springer series in operations research. | The network is small enough to optimise by inspection: capacity, lead time, and a scored feasible set. That is a model-based core with agents around it, which is the bridge Ivanov argues for. |

## ICARUS, as implemented here

- **Interaction.** Inventory, service, and sustainability read the same dictionaries. None of them keeps a private stock figure.
- **Creativity.** Four scenarios are first-class inputs: baseline, resin shortage, longer resin lead time, and a demand spike. The twin is for comparing them, not for producing one number.
- **Adaptation.** Each region’s level updates every week: `0.45 × actual + 0.55 × previous level`.
- **Reasoning.** Every committed row stores quantity, cost, and CO₂. The mode is a named policy: truck and expedite, rail only after backlog is cleared, or rail for every fair share.
- **Ubiquity.** Supplier capacity, plant stock, DC stock, and customer backlog are in one state object.
- **Synchronization.** One weekly clock ages every pipeline.

The Springer paper on digitalisation constraints in manufacturing (https://doi.org/10.1007/s00170-025-17202-2) is background for a limit this model states openly: a twin that assumes clean weekly data will overstate what a plant with late goods-receipts can automate. The CX PMO case in the sister repository is the data-quality layer this twin assumes already exists.
