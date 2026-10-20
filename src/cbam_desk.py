"""Sample CBAM declarant desk.

The arithmetic follows the published 2026 method: country default, the year's
mark-up, then the CBAM factor times the benchmark. Installation figures are
synthetic. A filing uses the Commission's Excel, not this file.
"""

from __future__ import annotations

from dataclasses import dataclass

# Article 21 price for imports in Q3 2026, published 5 October 2026.
CERTIFICATE_PRICE = 82.32

# Share of the benchmark still covered by free allocation. Withdrawn over time.
CBAM_FACTOR = {2026: 0.975, 2027: 0.95, 2028: 0.90, 2029: 0.775, 2030: 0.515}

# IR (EU) 2025/2621 as corrected: 10/20/30 percent, fertilisers stay at 1 percent.
MARKUP = {2026: 0.10, 2027: 0.20, 2028: 0.30, 2029: 0.30, 2030: 0.30}
FERTILISER_MARKUP = 0.01


@dataclass(frozen=True)
class Slice:
    """One installation's share of the imported tonne."""

    id: str
    tier: int
    role: str
    name: str
    place: str
    actual: float
    default_2026: float
    initial: str  # verified, unverified, unknown

    @property
    def known(self) -> bool:
        return self.initial != "unknown"


@dataclass(frozen=True)
class Line:
    id: str
    good: str
    cn: str
    sector: str
    origin: str
    customer: str
    promise: str
    tonnes: float
    route: str
    benchmark: float
    country_default: float
    default_note: str
    slices: tuple[Slice, ...]
    benchmark_note: str = ""


def markup(sector: str, year: int) -> float:
    if sector == "Fertilisers":
        return FERTILISER_MARKUP
    return MARKUP[year]


def slice_intensity(item: Slice, verified: set[str], sector: str, year: int) -> float:
    if item.id in verified:
        return item.actual
    scale = (1 + markup(sector, year)) / (1 + markup(sector, 2026))
    return item.default_2026 * scale


def intensity(line: Line, verified: set[str], year: int) -> float:
    return sum(slice_intensity(item, verified, line.sector, year) for item in line.slices)


def country_default_marked(line: Line, year: int) -> float:
    return line.country_default * (1 + markup(line.sector, year))


def certificates_per_tonne(embedded: float, line: Line, year: int) -> float:
    return max(0.0, embedded - CBAM_FACTOR[year] * line.benchmark)


def certificate_cost(embedded: float, line: Line, year: int) -> float:
    return certificates_per_tonne(embedded, line, year) * line.tonnes * CERTIFICATE_PRICE


def customer_position(line: Line, verified: set[str]) -> dict:
    """What the customer was promised, and whether that promise is still firm."""
    open_slices = [item for item in line.slices if item.id not in verified]
    date_open = any(item.tier == 1 for item in open_slices)
    price_open = bool(open_slices)
    if not open_slices:
        probability, impact = 1, 2
        complaint = "No open complaint. The quoted price can stand."
    elif date_open and any(item.initial == "unknown" for item in open_slices):
        probability, impact = 4, 5
        complaint = "The customer cannot be given a firm date or a firm price."
    elif price_open and line.tonnes >= 500:
        probability, impact = 3, 5
        complaint = "A certificate surcharge would change the order after the promise."
    else:
        probability, impact = 3, 3
        complaint = "The price stays open until the missing installation is verified."
    score = probability * impact
    band = "High" if score >= 15 else "Medium" if score >= 8 else "Low"
    return {
        "delivery": "Open" if date_open else "Held",
        "price": "Open" if price_open else "Firm",
        "complaint": complaint,
        "probability": probability,
        "impact": impact,
        "score": score,
        "band": band,
    }


def line_status(line: Line, verified: set[str]) -> str:
    states = ["verified" if item.id in verified else item.initial for item in line.slices]
    if all(state == "verified" for state in states):
        return "Verified"
    if any(state == "verified" for state in states):
        return "Partial"
    return "Default only"


def initial_verified() -> set[str]:
    return {item.id for line in LINES for item in line.slices if item.initial == "verified"}


def saving_if_verified(line: Line, item: Slice, verified: set[str], year: int) -> float:
    if item.id in verified:
        return 0.0
    before = certificate_cost(intensity(line, verified, year), line, year)
    after = certificate_cost(intensity(line, verified | {item.id}, year), line, year)
    return before - after


LINES: tuple[Line, ...] = (
    Line(
        id="L-01",
        good="Hot-rolled coil",
        cn="7208 39 00",
        sector="Iron and steel",
        origin="India",
        customer="German body-panel account",
        promise="Coil in the quoted week, at the quoted price",
        tonnes=1800,
        route="BF-BOF",
        benchmark=1.370,
        country_default=4.28,
        default_note="Public calculators list 4.28 tCO2e/t for India, CN 7208 39 00, before the 2026 mark-up. A declaration uses the Commission Excel.",
        slices=(
            Slice("L01-mill", 1, "Mill", "Deccan Flat Products", "Jamshedpur, sample mill", 0.85, 1.40, "verified"),
            Slice("L01-iron", 2, "Precursor", "Hot metal, same works", "Jamshedpur", 0.78, 1.35, "verified"),
            Slice("L01-coke", 2, "Precursor", "East Gate Coke", "Jharkhand, sample plant", 0.32, 0.55, "verified"),
            Slice("L01-ore", 3, "Extraction", "Singhbhum iron fines", "Odisha, named, no verifier report", 0.22, 0.48, "unverified"),
            Slice("L01-coal", 3, "Extraction", "Coking coal, installation not on the invoice", "Bought through Harbour Bulk, Singapore", 0.35, 0.928, "unknown"),
        ),
    ),
    Line(
        id="L-02",
        good="Steel slab",
        cn="7207 12 10",
        sector="Iron and steel",
        origin="China",
        customer="Appliance housing account",
        promise="Slab available for the production slot already confirmed",
        tonnes=900,
        route="BF-BOF",
        benchmark=1.364,
        country_default=3.169,
        default_note="Published country default for China, CN 7207 12 10: 3.169 tCO2e/t before mark-up. BF-BOF benchmark 1.364.",
        slices=(
            Slice("L02-mill", 1, "Mill", "Hebei Heat Metals", "Hebei, sample mill, sheet not verified", 0.72, 1.20, "unverified"),
            Slice("L02-iron", 2, "Precursor", "Blast-furnace hot metal", "Same site, unverified", 0.64, 1.10, "unverified"),
            Slice("L02-coke", 2, "Precursor", "Coke battery", "Same site, unverified", 0.25, 0.45, "unverified"),
            Slice("L02-coal", 3, "Extraction", "Coking coal mine", "Not named by the mill", 0.30, 0.7359, "unknown"),
        ),
    ),
    Line(
        id="L-03",
        good="Wire rod",
        cn="7213 10 00",
        sector="Iron and steel",
        origin="Origin not established",
        customer="Spot buyer",
        promise="No date and no price can be confirmed",
        tonnes=320,
        route="BF-BOF",
        benchmark=1.370,
        country_default=4.049,
        default_note="No country table can be chosen. The desk uses the published 'other countries and territories' figure for this kind of hot-rolled product, 4.049 tCO2e/t before mark-up.",
        slices=(
            Slice("L03-mill", 1, "Mill", "Mill not named", "Trader bill of lading only", 0.90, 1.80, "unknown"),
            Slice("L03-iron", 2, "Precursor", "Hot metal", "Installation unknown", 0.70, 1.40, "unknown"),
            Slice("L03-coke", 2, "Precursor", "Coke", "Installation unknown", 0.28, 0.55, "unknown"),
            Slice("L03-coal", 3, "Extraction", "Coking coal", "Installation unknown", 0.32, 0.7039, "unknown"),
        ),
    ),
    Line(
        id="L-04",
        good="Urea",
        cn="3102 10 19",
        sector="Fertilisers",
        origin="Egypt",
        customer="Blending account",
        promise="Urea at the quoted contribution margin",
        tonnes=600,
        route="Ammonia synthesis",
        benchmark=0.0,
        country_default=1.390,
        default_note="Published example for Egypt, CN 3102 10 19: 1.390 tCO2e/t before the 1% fertiliser mark-up. The legal functional unit is kilograms of nitrogen.",
        benchmark_note="No benchmark is deducted on this sample line. The fertiliser functional unit is kilograms of nitrogen, and this desk does not invent that benchmark.",
        slices=(
            Slice("L04-plant", 1, "Plant", "Nile Nutrient Chemicals", "Sample ammonia-urea plant, sheet not verified", 0.62, 0.95, "unverified"),
            Slice("L04-gas", 3, "Extraction", "Natural gas field", "Not named behind the ammonia", 0.22, 0.4539, "unknown"),
        ),
    ),
    Line(
        id="L-05",
        good="Unwrought aluminium",
        cn="7601",
        sector="Aluminium",
        origin="United Arab Emirates",
        customer="Adhesive cartridge account",
        promise="Aluminium for the pack the customer receives, at the quoted price",
        tonnes=120,
        route="Smelter",
        benchmark=0.0,
        country_default=1.870,
        default_note="Published example for the UAE and Bahrain, CN 7601: 1.870 tCO2e/t before mark-up. Aluminium is priced on direct emissions, including PFCs.",
        benchmark_note="No aluminium benchmark is deducted here. The sample keeps the comparison to the marked default.",
        slices=(
            Slice("L05-smelt", 1, "Smelter", "Gulf Primary Aluminium", "Sample smelter, unverified", 1.05, 1.40, "unverified"),
            Slice("L05-alumina", 2, "Precursor", "Alumina refinery", "Named, no verifier report", 0.28, 0.40, "unverified"),
            Slice("L05-bauxite", 3, "Extraction", "Bauxite mine", "Not named", 0.12, 0.257, "unknown"),
        ),
    ),
    Line(
        id="L-06",
        good="Grey Portland cement",
        cn="2523 29 00",
        sector="Cement",
        origin="Türkiye",
        customer="Site-works account",
        promise="Cement for the scheduled pour, at the quoted price",
        tonnes=250,
        route="Kiln",
        benchmark=0.666,
        country_default=1.440,
        default_note="Published 'other countries and territories' value used for this CN code, 1.440 tCO2e/t before mark-up. Benchmark cited for this cement: 0.666.",
        slices=(
            Slice("L06-kiln", 1, "Kiln", "Anatolian Grey Kiln", "Sample kiln, unverified", 0.72, 1.10, "unverified"),
            Slice("L06-clinker", 2, "Precursor", "Clinker, same site", "Unverified", 0.18, 0.30, "unverified"),
            Slice("L06-quarry", 3, "Extraction", "Limestone quarry", "Named with the kiln", 0.08, 0.184, "verified"),
        ),
    ),
    Line(
        id="L-07",
        good="Hydrogen",
        cn="2804 10 00",
        sector="Hydrogen",
        origin="No country table",
        customer="Process-heat account",
        promise="Hydrogen for the booked process window, at the quoted price",
        tonnes=5,
        route="Steam reforming",
        benchmark=0.0,
        country_default=17.740,
        default_note="Published 'other countries and territories' value, CN 2804 10 00: 17.740 tCO2e/t before mark-up.",
        benchmark_note="No hydrogen benchmark is deducted in this sample.",
        slices=(
            Slice("L07-smr", 1, "Plant", "Atlas Gas Chemicals", "Sample reformer, unverified", 9.0, 12.0, "unverified"),
            Slice("L07-gas", 3, "Extraction", "Natural gas field", "Not named", 2.5, 7.514, "unknown"),
        ),
    ),
)


def book_cost(verified: set[str], year: int, mode: str, sector: str | None = None) -> float:
    total = 0.0
    for line in LINES:
        if sector and line.sector != sector:
            continue
        if mode == "default":
            embedded = country_default_marked(line, year)
        elif mode == "full":
            embedded = intensity(line, {item.id for item in line.slices}, year)
        else:
            embedded = intensity(line, verified, year)
        total += certificate_cost(embedded, line, year)
    return total


def actions(verified: set[str], year: int) -> list[dict]:
    rows = []
    for line in LINES:
        for item in line.slices:
            euros = saving_if_verified(line, item, verified, year)
            if euros <= 1:
                continue
            verb = "Name the installation and verify it" if item.initial == "unknown" else "Obtain the verifier's report"
            rows.append(
                {
                    "euros": euros,
                    "line": line.id,
                    "good": line.good,
                    "slice": item.id,
                    "who": item.name,
                    "place": item.place,
                    "tier": item.tier,
                    "verb": verb,
                }
            )
    rows.sort(key=lambda row: row["euros"], reverse=True)
    return rows
