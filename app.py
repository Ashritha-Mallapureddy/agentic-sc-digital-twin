"""Scenario explorer for the agentic twin."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "data" / "scenario_results.json"

st.set_page_config(page_title="Agentic supply chain twin", layout="wide")

if not JSON_PATH.exists():
    from src.twin import main

    main()

results = json.loads(JSON_PATH.read_text())
summary = pd.DataFrame(
    [
        {
            "scenario": item["scenario"],
            "mode": item["mode"],
            "fill_rate": item["fill_rate"],
            "ending_backlog": item["ending_backlog"],
            "cost": item["cost"],
            "co2": item["co2"],
            "rail_share": item["rail_share"],
            "expedite_qty": item["expedite_qty"],
        }
        for item in results
    ]
)

st.title("Agentic digital twin")
st.caption(
    "SRH supply-chain project. Synthetic network: resin, packaging, Cologne plant, Duisburg DC. "
    "Agents share one state. CO₂ figures are model units."
)

scenario = st.sidebar.selectbox("Scenario", ["baseline", "resin_short", "port_delay", "demand_spike"])
mode = st.sidebar.radio("Orchestrator weights", ["balanced", "service", "low_carbon"])
chosen = next(item for item in results if item["scenario"] == scenario and item["mode"] == mode)
weeks = pd.DataFrame(chosen["weeks"])

cols = st.columns(4)
cols[0].metric("Fill rate", f"{chosen['fill_rate']:.1%}")
cols[1].metric("Ending backlog", f"{chosen['ending_backlog']:.0f}")
cols[2].metric("Cost", f"{chosen['cost']:.0f}")
cols[3].metric("CO₂", f"{chosen['co2']:.0f}")

long = weeks.melt("week", value_vars=["demand", "served", "backlog"], var_name="series", value_name="kits")
fig = px.line(long, x="week", y="kits", color="series", markers=True)
fig.update_layout(height=380, margin=dict(l=10, r=10, t=20, b=10))
st.plotly_chart(fig, use_container_width=True)

st.subheader("All scenarios")
show = summary.copy()
show["fill_rate"] = show["fill_rate"].map(lambda value: f"{value:.1%}")
show["rail_share"] = show["rail_share"].map(lambda value: f"{value:.0%}")
st.dataframe(show, use_container_width=True, hide_index=True)

st.subheader(f"Actions in week {int(weeks.iloc[-1].week)} are below. Pick a week to see why the orchestrator committed.")
week_no = st.slider("Week", 1, int(weeks["week"].max()), 8)
actions = weeks.loc[weeks["week"] == week_no, "actions"].iloc[0]
st.dataframe(pd.DataFrame(actions), use_container_width=True, hide_index=True)

with st.expander("How the agents divide the work"):
    st.markdown(
        """
        Inventory can produce, move finished goods to Duisburg the same week, and replenish.
        The DC is split across regions in proportion to backlog plus forecast.
        Service sends that share by truck and may expedite from a small plant buffer.
        Low-carbon sends the same share by rail. Balanced uses rail only after a region's backlog is gone.
        Disruption rewrites resin capacity or lead time. It does not get a vote.
        """
    )
