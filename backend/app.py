"""
Smart Rooftop Rainwater Harvesting and Groundwater Recharge Assessment System
Backend API — Flask
"""

import json
import math
import os

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

with open(os.path.join(_DATA_DIR, "rainfall.json"), encoding="utf-8") as _f:
    RAINFALL_DATA: dict[str, int] = json.load(_f)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

RUNOFF_COEFFICIENT = 0.8  # CGWB recommended value for rooftop surfaces

STRUCTURE_COSTS = {
    "Recharge pit": 5000,
    "Recharge trench": 7000,
    "Recharge shaft": 7000,
    "Storage tank": 10000,
}

AQUIFER_TYPES = [
    "Alluvium (sand & gravel)",
    "Basalt",
    "Granite gneiss",
    "Laterite",
    "Sandstone",
]

POLICIES = [
    "25% subsidy on recharge pits under state groundwater conservation scheme.",
    "Property tax rebate for certified rainwater harvesting installations.",
    "CGWB advisory: priority funding for groundwater-stressed wards.",
    "District scheme: ₹15,000 assistance for recharge shafts in rural areas.",
    "Urban local body: free technical consultation for RTRWH units.",
]

VENDORS = [
    {"name": "RainCharge Solutions", "rating": 4.8, "city": "Pan-India"},
    {"name": "Jal Rakshak Engineers", "rating": 4.6, "city": "North India"},
    {"name": "Green Roof Tech", "rating": 4.7, "city": "South India"},
    {"name": "HydroEarth Services", "rating": 4.5, "city": "West India"},
    {"name": "Varshadhara Constructions", "rating": 4.4, "city": "East India"},
]

LEADERBOARD = [
    {"rank": 1, "name": "Green Valley Society", "city": "Pune", "credits": 4200, "litersRecharged": 420000},
    {"rank": 2, "name": "Eco Homes Block B", "city": "Chennai", "credits": 3800, "litersRecharged": 380000},
    {"rank": 3, "name": "Sunrise Apartments", "city": "Bangalore", "credits": 3500, "litersRecharged": 350000},
    {"rank": 4, "name": "Blue Lake Colony", "city": "Kolkata", "credits": 3200, "litersRecharged": 320000},
    {"rank": 5, "name": "River View Complex", "city": "Mumbai", "credits": 2900, "litersRecharged": 290000},
]

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def _hash_seed(text: str) -> int:
    """Simple deterministic hash used to produce mock location-specific data."""
    return sum(ord(c) for c in text)


def _get_rainfall(location: str) -> int:
    """Return annual rainfall (mm) for a location using city lookup or hash fallback."""
    location_lower = location.lower().strip()
    for city, mm in RAINFALL_DATA.items():
        if city in location_lower or location_lower.startswith(city):
            return mm
    # Deterministic fallback based on string hash
    seed = _hash_seed(location_lower) if location_lower else 500
    return 700 + (seed % 700)


def _get_aquifer(location: str) -> str:
    seed = _hash_seed(location or "default")
    return AQUIFER_TYPES[seed % len(AQUIFER_TYPES)]


def _get_groundwater_depth(location: str) -> str:
    seed = _hash_seed(location or "depth")
    low = 8 + (seed % 6)
    return f"{low}-{low + 6} m below ground level"


def _get_policy(location: str) -> str:
    seed = _hash_seed((location or "") + "policy")
    return POLICIES[seed % len(POLICIES)]


def _decide_structure(open_space: float) -> str:
    if open_space >= 25:
        return "Recharge pit"
    if open_space >= 12:
        return "Recharge trench"
    return "Recharge shaft"


def _calculate_dimensions(structure: str, volume_m3: float) -> str:
    if structure == "Recharge pit":
        depth = 2.0
        side = math.sqrt(max(volume_m3, 0.01) / depth)
        return f"{side:.1f} m \u00d7 {side:.1f} m \u00d7 {depth:.1f} m"
    if structure == "Recharge trench":
        depth, width = 1.5, 1.2
        length = max(volume_m3, 0.01) / (depth * width)
        return f"{length:.1f} m \u00d7 {width:.1f} m \u00d7 {depth:.1f} m"
    # Recharge shaft (cylindrical)
    radius = 0.6
    depth = max(volume_m3, 0.01) / (math.pi * radius ** 2)
    return f"{depth:.1f} m depth \u00d7 {radius * 2:.1f} m diameter"


# Short-name aliases for the /cost endpoint
_TYPE_ALIASES = {
    "pit": "Recharge pit",
    "trench": "Recharge trench",
    "shaft": "Recharge shaft",
    "tank": "Storage tank",
}

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.route("/calculate", methods=["POST"])
def calculate():
    """
    Calculate runoff and harvested water potential.

    Request body (JSON):
      roofArea / roof_area   float   Roof area in m²
      location               str     City / location name
      dwellers               int     Number of dwellers
      rainfall               float?  Annual rainfall in mm (optional; derived from location if absent)

    Response (JSON):
      annualRainfallMm, runoffLiters, harvestedWaterLiters,
      waterDemandLiters, feasible, runoffCoefficient,
      aquifer, groundwaterDepth, policy
    """
    body = request.get_json(force=True) or {}
    # Accept both camelCase and snake_case for roof area
    raw_area = body.get("roofArea", body.get("roof_area", 100))
    try:
        roof_area = float(raw_area)
    except (TypeError, ValueError):
        return jsonify({"error": "roofArea must be a number"}), 400
    if roof_area <= 0:
        return jsonify({"error": "roofArea must be greater than 0"}), 400
    location = str(body.get("location", ""))
    dwellers = max(1, int(body.get("dwellers", 4)))
    rainfall_override = body.get("rainfall")

    annual_rainfall = float(rainfall_override) if rainfall_override else _get_rainfall(location)

    # Harvested Water = Roof Area × Rainfall (m) × Runoff Coefficient
    # rainfall is in mm → divide by 1000 for metres, then × 1000 for litres → net factor 1
    runoff_liters = roof_area * annual_rainfall * RUNOFF_COEFFICIENT

    # Rough household demand: 150 L/person/day
    water_demand_liters = dwellers * 150 * 365

    feasible = runoff_liters >= water_demand_liters * 0.2

    return jsonify(
        {
            "annualRainfallMm": annual_rainfall,
            "runoffLiters": round(runoff_liters),
            "harvestedWaterLiters": round(runoff_liters),
            "waterDemandLiters": water_demand_liters,
            "feasible": feasible,
            "runoffCoefficient": RUNOFF_COEFFICIENT,
            "aquifer": _get_aquifer(location),
            "groundwaterDepth": _get_groundwater_depth(location),
            "policy": _get_policy(location),
        }
    )


@app.route("/recommend", methods=["POST"])
def recommend():
    """
    Recommend a recharge structure and dimensions.

    Request body (JSON):
      openSpace / roof_area   float   Available open space in m² (or roof area as proxy)
      runoff                  float   Annual runoff in litres

    Response (JSON):
      structure, dimensions, rechargeVolumeM3
    """
    body = request.get_json(force=True) or {}
    # Accept roof_area as an alias — estimate open space as 25% of roof area
    raw_space = body.get("openSpace", body.get("open_space"))
    raw_roof = body.get("roofArea", body.get("roof_area"))
    if raw_space is not None:
        open_space = float(raw_space)
    elif raw_roof is not None:
        open_space = float(raw_roof) * 0.25
    else:
        open_space = 10.0
    if open_space < 0:
        return jsonify({"error": "openSpace must be 0 or greater"}), 400
    runoff_liters = float(body.get("runoff", 50000))

    structure = _decide_structure(open_space)
    recharge_volume_m3 = max(0.1, runoff_liters / 1_000_000 * 300)  # 30% of runoff in m³
    dimensions = _calculate_dimensions(structure, recharge_volume_m3)

    return jsonify(
        {
            "structure": structure,
            "dimensions": dimensions,
            "rechargeVolumeM3": round(recharge_volume_m3, 2),
        }
    )


@app.route("/cost", methods=["POST"])
def cost():
    """
    Estimate installation cost and cost-benefit analysis.

    Request body (JSON):
      structure / type   str     Structure type (full name or short alias: pit/trench/shaft/tank)
      runoff             float   Annual runoff in litres

    Response (JSON):
      structure, costRs, annualSavingsRs, paybackYears,
      environmentalBenefitLiters, carbonOffsetKg
    """
    body = request.get_json(force=True) or {}
    raw_type = body.get("structure", body.get("type", "Recharge pit"))
    # Resolve short aliases (e.g. "pit" → "Recharge pit")
    structure = _TYPE_ALIASES.get(str(raw_type).lower(), raw_type)
    runoff_liters = float(body.get("runoff", 50000))

    base_cost = STRUCTURE_COSTS.get(structure, 5000)

    # Water savings: ₹0.05 per litre (average urban water tariff)
    annual_savings = runoff_liters * 0.05
    payback_years = round(base_cost / annual_savings, 1) if annual_savings > 0 else 999

    return jsonify(
        {
            "structure": structure,
            "costRs": base_cost,
            "annualSavingsRs": round(annual_savings),
            "paybackYears": payback_years,
            "environmentalBenefitLiters": round(runoff_liters),
            "carbonOffsetKg": round(runoff_liters * 0.0002),
        }
    )


@app.route("/rainfall", methods=["GET"])
def rainfall():
    """
    Get annual rainfall data for a city.

    Query params:
      city   str   City / location name

    Response (JSON):
      city, annualRainfallMm, source
    """
    city = request.args.get("city", "").strip()
    annual_rainfall = _get_rainfall(city)
    return jsonify(
        {
            "city": city,
            "annualRainfallMm": annual_rainfall,
            "source": "CGWB Mock Data",
        }
    )


@app.route("/leaderboard", methods=["GET"])
def leaderboard():
    """
    Return the water credit leaderboard and aggregate impact.

    Response (JSON):
      leaderboard[], totalLitersRecharged, olympicPoolsEquivalent
    """
    total = sum(e["litersRecharged"] for e in LEADERBOARD)
    return jsonify(
        {
            "leaderboard": LEADERBOARD,
            "totalLitersRecharged": total,
            "olympicPoolsEquivalent": round(total / 2_500_000, 1),
        }
    )


@app.route("/vendors", methods=["GET"])
def vendors():
    """Return a list of local vendors."""
    return jsonify({"vendors": VENDORS})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
