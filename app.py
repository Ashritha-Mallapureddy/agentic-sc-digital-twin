"""CBAM declarant desk. Sample book for an EU importer of steel and the other covered goods."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.cbam_desk import (
    CBAM_FACTOR,
    CERTIFICATE_PRICE,
    LINES,
    actions,
    book_cost,
    certificates_per_tonne,
    country_default_marked,
    customer_position,
    initial_verified,
    intensity,
    line_status,
    markup,
    slice_intensity,
)

st.set_page_config(page_title="CBAM desk", layout="wide", initial_sidebar_state="expanded")
st.markdown(
    """
    <style>
    header[data-testid="stHeader"] { background: #0e1c2f; }
    [data-testid="stSidebar"] { background: #0e1c2f; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #e7edf5; }
    [data-testid="stSidebar"] .stCaption { color: #b7c3d4; }
    .block-container { padding-top: 1.1rem; max-width: 1180px; }
    div[data-testid="stMetric"] {
        background: white; border: 1px solid #e3e8ef; border-top: 3px solid #0e1c2f;
        padding: 12px 14px;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "verified" not in st.session_state:
    st.session_state.verified = initial_verified()
if "page" not in st.session_state:
    st.session_state.page = "Exposure"
if "line" not in st.session_state:
    st.session_state.line = LINES[0].id

with st.sidebar:
    st.markdown("**CBAM desk**")
    st.caption("Linea Automotive GmbH · Düsseldorf · sample declarant, not a filing")
    year = st.selectbox("Declaration year", [2026, 2027, 2028, 2029, 2030], index=0)
    st.caption(
        f"Certificate price held at €{CERTIFICATE_PRICE:.2f}. "
        "That is the Q3 2026 price published on 5 October 2026. "
        f"Mark-up this year {markup('Iron and steel', year):.0%}. "
        f"CBAM factor {CBAM_FACTOR[year]:.1%}."
    )
    st.divider()
    for name in ("Exposure", "Import book", "Supplier chain", "Agents"):
        if st.button(name, width="stretch", type="primary" if st.session_state.page == name else "secondary"):
            st.session_state.page = name
            st.rerun()

verified: set[str] = st.session_state.verified
page = st.session_state.page
by_id = {line.id: line for line in LINES}


def euros(value: float) -> str:
    return f"€{value:,.0f}"


def line_embedded(line, mode: str) -> float:
    if mode == "default":
        return country_default_marked(line, year)
    if mode == "full":
        return intensity(line, {item.id for item in line.slices}, year)
    return intensity(line, verified, year)


def cost_of(line, mode: str) -> float:
    return certificates_per_tonne(line_embedded(line, mode), line, year) * line.tonnes * CERTIFICATE_PRICE


if page == "Exposure":
    st.markdown("## Decision for the customer-experience review")
    positions = [customer_position(line, verified) for line in LINES]
    open_price = sum(1 for item in positions if item["price"] == "Open")
    open_date = sum(1 for item in positions if item["delivery"] == "Open")
    default_cost = book_cost(verified, year, "default")
    today_cost = book_cost(verified, year, "today")
    full_cost = book_cost(verified, year, "full")
    st.markdown(
        "A customer-experience PMO puts one page in front of leadership: the promise to the customer, "
        "and the cost that can break that promise. In 2026 the cost includes CBAM certificates on steel, "
        "fertilisers, aluminium, cement and hydrogen. The certificate is still paid. "
        "The mark-up appears only where a mill, a coke plant, a coal mine or a gas field is not verified, "
        "and that is what turns a quoted price into an order change."
    )
    p1, p2, p3 = st.columns(3)
    p1.metric("Promises with an open price", f"{open_price} of {len(LINES)}")
    p2.metric("Promises with an open date", f"{open_date} of {len(LINES)}")
    p3.metric("Mark-up still in the book", euros(today_cost - full_cost))
    st.caption(
        "Open price is an order change waiting to happen (Auftragsänderung). "
        "Open date is the delivery promise at risk (Liefertreue). "
        "A surcharge after the order is the complaint (Reklamation). "
        "The euro figure is the certificate mark-up, not a forecast of revenue."
    )
    tonnes = sum(line.tonnes for line in LINES)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tonnes", f"{tonnes:,.0f}")
    c2.metric("Country default", euros(default_cost))
    c3.metric("Chain today", euros(today_cost))
    c4.metric("Fully verified", euros(full_cost))
    st.caption(
        f"Certificates per tonne = embedded emissions − {CBAM_FACTOR[year]:.1%} × benchmark, then × €{CERTIFICATE_PRICE:.2f}. "
        "Fertiliser, aluminium and hydrogen lines in this sample do not deduct a benchmark, and the screen says so on those lines. "
        "Article 9 (a carbon price already paid) is zero in this book: none of these origins is given a recognised deduction here."
    )

    chart = pd.DataFrame(
        [
            {
                "Line": line.id,
                "Country default": cost_of(line, "default"),
                "Chain today": cost_of(line, "today"),
                "Fully verified": cost_of(line, "full"),
            }
            for line in LINES
        ]
    )
    figure = go.Figure()
    figure.add_bar(name="Country default", x=chart["Line"], y=chart["Country default"], marker_color="#8d97a5")
    figure.add_bar(name="Chain today", x=chart["Line"], y=chart["Chain today"], marker_color="#1f4e79")
    figure.add_bar(name="Fully verified", x=chart["Line"], y=chart["Fully verified"], marker_color="#0f7b4c")
    figure.update_layout(
        barmode="group",
        height=380,
        margin=dict(l=10, r=10, t=30, b=40),
        legend=dict(orientation="h", y=1.12),
        yaxis_title="Certificate cost, euro",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="white",
        font=dict(family="Segoe UI, sans-serif", size=13),
    )
    st.plotly_chart(figure, width="stretch")
    st.caption(
        "Grey is the bill if the declarant files country defaults. "
        "Blue is the bill the evidence in the book can support today. "
        "Green is the bill after the unknown mine, quarry or gas field is named and verified. "
        + " · ".join(f"{line.id} {line.good}" for line in LINES)
    )

elif page == "Import book":
    st.markdown("## Import book")
    st.markdown("One row is one customs line. Open a line on the supplier-chain page to see who sits behind it.")
    sector = st.selectbox("Sector", ["All covered goods", *dict.fromkeys(line.sector for line in LINES)])
    rows = []
    for line in LINES:
        if sector != "All covered goods" and line.sector != sector:
            continue
        rows.append(
            {
                "Line": line.id,
                "Good": line.good,
                "CN": line.cn,
                "Sector": line.sector,
                "Origin": line.origin,
                "Tonnes": line.tonnes,
                "Status": line_status(line, verified),
                "Default €": round(cost_of(line, "default")),
                "Today €": round(cost_of(line, "today")),
                "Verified €": round(cost_of(line, "full")),
            }
        )
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
    unknown = [
        f"{line.id} · {item.name}"
        for line in LINES
        for item in line.slices
        if item.id not in verified and item.initial == "unknown" and (sector == "All covered goods" or line.sector == sector)
    ]
    st.markdown("**Installations the invoice does not name**")
    st.write(", ".join(unknown) if unknown else "Every extraction tier in the current filter is named.")

elif page == "Supplier chain":
    st.markdown("## Supplier chain")
    st.markdown(
        "Tier 1 is the plant on the invoice. Tier 2 is the precursor that plant consumes. "
        "Tier 3 is the extraction the importer never contracts: the coal, the ore, the gas. "
        "A verified slice uses the installation figure. Anything else stays on the marked default."
    )
    choice = st.selectbox(
        "Line",
        [line.id for line in LINES],
        index=[line.id for line in LINES].index(st.session_state.line),
        format_func=lambda key: f"{key} · {by_id[key].good} · {by_id[key].origin}",
    )
    st.session_state.line = choice
    line = by_id[choice]
    embedded = intensity(line, verified, year)
    st.caption(line.default_note)
    if line.benchmark_note:
        st.caption(line.benchmark_note)
    a, b, c = st.columns(3)
    a.metric("Embedded emissions used", f"{embedded:.3f} tCO2e/t")
    b.metric("Country default, marked up", f"{country_default_marked(line, year):.3f} tCO2e/t")
    c.metric("Certificate cost today", euros(cost_of(line, "today")))

    st.markdown(f"**Declarant** · Linea Automotive GmbH · {line.tonnes:,.0f} t of {line.good} · CN {line.cn}")
    for tier, title in ((1, "Tier 1 · the plant on the invoice"), (2, "Tier 2 · precursors"), (3, "Tier 3 · extraction, often unnamed")):
        group = [item for item in line.slices if item.tier == tier]
        if not group:
            continue
        st.markdown(f"**{title}**")
        columns = st.columns(len(group))
        for column, item in zip(columns, group):
            state = "verified" if item.id in verified else item.initial
            used = slice_intensity(item, verified, line.sector, year)
            with column:
                with st.container(border=True):
                    st.markdown(f"**{item.role}**")
                    st.write(item.name)
                    st.caption(item.place)
                    st.write(f"{used:.3f} tCO2e/t")
                    if state == "verified":
                        st.success("Verified actual")
                    elif state == "unknown":
                        st.error("Installation unknown")
                        if st.button("Name it and use the actual", key=f"ok-{item.id}"):
                            st.session_state.verified = verified | {item.id}
                            st.rerun()
                    else:
                        st.warning("Named, not verified")
                        if st.button("Attach the verifier report", key=f"ok-{item.id}"):
                            st.session_state.verified = verified | {item.id}
                            st.rerun()

else:
    st.markdown("## Agents")
    st.markdown(
        "Four agents read the same book. None of them removes a certificate that the verified figure still requires. "
        "They remove the mark-up that exists only because an installation is missing."
    )
    findings = actions(verified, year)
    unknown_count = sum(1 for line in LINES for item in line.slices if item.initial == "unknown" and item.id not in verified)
    cols = st.columns(4)
    cols[0].metric("Customs reader", f"{len(LINES)} lines")
    cols[1].metric("Chain scout", f"{unknown_count} unnamed")
    cols[2].metric("Emissions clerk", euros(book_cost(verified, year, "today")))
    cols[3].metric("Certificate desk", f"{len(findings)} actions")
    st.markdown(
        f"The customs reader holds {sum(line.tonnes for line in LINES):,.0f} tonnes, above the 50-tonne threshold, "
        "so this sample importer needs authorised-declarant status. "
        f"The chain scout still cannot name {unknown_count} extraction sites. "
        "The emissions clerk will not use an actual figure until that site is verified. "
        "The certificate desk ranks the sites by the euro the mark-up is adding."
    )
    if not findings:
        st.success("Every installation in the book is verified. The remaining certificate cost is the actual embedded emissions, priced at the published certificate.")
    for row in findings:
        with st.container(border=True):
            left, right = st.columns([5, 1])
            left.markdown(
                f"**{row['verb']}** · {row['line']} {row['good']}  \n"
                f"{row['who']} · {row['place']} · tier {row['tier']}"
            )
            right.metric("Removes", euros(row["euros"]))
            if st.button("Record it as verified", key=f"act-{row['slice']}"):
                st.session_state.verified = verified | {row["slice"]}
                st.rerun()
    if st.button("Reset the book to the evidence we started with"):
        st.session_state.verified = initial_verified()
        st.rerun()
