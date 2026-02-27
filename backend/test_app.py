"""
Automated tests for the Smart RTRWH Flask backend.
Run with: pytest test_app.py -v
"""

import json
import pytest

from app import app as flask_app


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


# ---------------------------------------------------------------------------
# /health
# ---------------------------------------------------------------------------

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"


# ---------------------------------------------------------------------------
# /calculate
# ---------------------------------------------------------------------------

def test_calculate_basic(client):
    r = client.post(
        "/calculate",
        data=json.dumps({"roofArea": 100, "location": "kolkata"}),
        content_type="application/json",
    )
    assert r.status_code == 200
    data = r.get_json()
    # Kolkata rainfall = 1600 mm; 100 × 1600 × 0.8 = 128 000
    assert data["harvestedWaterLiters"] == 128000
    assert data["annualRainfallMm"] == 1600
    assert data["runoffCoefficient"] == 0.8
    assert "aquifer" in data
    assert "groundwaterDepth" in data
    assert "policy" in data


def test_calculate_snake_case(client):
    """roof_area (snake_case) must be accepted."""
    r = client.post(
        "/calculate",
        data=json.dumps({"roof_area": 200, "location": "mumbai"}),
        content_type="application/json",
    )
    assert r.status_code == 200
    data = r.get_json()
    # Mumbai rainfall = 2200; 200 × 2200 × 0.8 = 352 000
    assert data["harvestedWaterLiters"] == 352000


def test_calculate_zero_area(client):
    r = client.post(
        "/calculate",
        data=json.dumps({"roofArea": 0, "location": "delhi"}),
        content_type="application/json",
    )
    assert r.status_code == 400
    assert "error" in r.get_json()


def test_calculate_negative_area(client):
    r = client.post(
        "/calculate",
        data=json.dumps({"roofArea": -50, "location": "delhi"}),
        content_type="application/json",
    )
    assert r.status_code == 400


def test_calculate_rainfall_override(client):
    r = client.post(
        "/calculate",
        data=json.dumps({"roofArea": 50, "location": "delhi", "rainfall": 1000}),
        content_type="application/json",
    )
    assert r.status_code == 200
    data = r.get_json()
    assert data["annualRainfallMm"] == 1000
    assert data["harvestedWaterLiters"] == round(50 * 1000 * 0.8)


def test_calculate_empty_body(client):
    r = client.post(
        "/calculate",
        data=json.dumps({}),
        content_type="application/json",
    )
    assert r.status_code == 200
    data = r.get_json()
    # Default roofArea=100, default location uses hash fallback
    assert "harvestedWaterLiters" in data
    assert data["harvestedWaterLiters"] > 0
    assert "aquifer" in data
    assert "groundwaterDepth" in data


# ---------------------------------------------------------------------------
# /recommend
# ---------------------------------------------------------------------------

def test_recommend_pit(client):
    """open space >= 25 m² → Recharge pit."""
    r = client.post(
        "/recommend",
        data=json.dumps({"openSpace": 30, "runoff": 100000}),
        content_type="application/json",
    )
    assert r.status_code == 200
    data = r.get_json()
    assert data["structure"] == "Recharge pit"


def test_recommend_trench(client):
    """12 <= open space < 25 m² → Recharge trench."""
    r = client.post(
        "/recommend",
        data=json.dumps({"openSpace": 15, "runoff": 50000}),
        content_type="application/json",
    )
    assert r.status_code == 200
    assert r.get_json()["structure"] == "Recharge trench"


def test_recommend_shaft(client):
    """open space < 12 m² → Recharge shaft."""
    r = client.post(
        "/recommend",
        data=json.dumps({"openSpace": 5, "runoff": 20000}),
        content_type="application/json",
    )
    assert r.status_code == 200
    assert r.get_json()["structure"] == "Recharge shaft"


def test_recommend_via_roof_area(client):
    """roof_area=100 → open_space=25 → Recharge pit."""
    r = client.post(
        "/recommend",
        data=json.dumps({"roof_area": 100}),
        content_type="application/json",
    )
    assert r.status_code == 200
    assert r.get_json()["structure"] == "Recharge pit"


def test_recommend_negative_open_space(client):
    r = client.post(
        "/recommend",
        data=json.dumps({"openSpace": -5}),
        content_type="application/json",
    )
    assert r.status_code == 400


# ---------------------------------------------------------------------------
# /cost
# ---------------------------------------------------------------------------

def test_cost_pit(client):
    r = client.post(
        "/cost",
        data=json.dumps({"type": "pit", "runoff": 50000}),
        content_type="application/json",
    )
    assert r.status_code == 200
    data = r.get_json()
    assert data["costRs"] == 5000
    assert data["structure"] == "Recharge pit"


def test_cost_tank(client):
    r = client.post(
        "/cost",
        data=json.dumps({"type": "tank", "runoff": 50000}),
        content_type="application/json",
    )
    assert r.status_code == 200
    assert r.get_json()["costRs"] == 10000


def test_cost_trench(client):
    r = client.post(
        "/cost",
        data=json.dumps({"type": "trench", "runoff": 80000}),
        content_type="application/json",
    )
    assert r.status_code == 200
    assert r.get_json()["costRs"] == 7000


def test_cost_full_name(client):
    r = client.post(
        "/cost",
        data=json.dumps({"structure": "Recharge shaft", "runoff": 40000}),
        content_type="application/json",
    )
    assert r.status_code == 200
    data = r.get_json()
    assert data["costRs"] == 7000
    assert "annualSavingsRs" in data
    assert "paybackYears" in data
    assert "carbonOffsetKg" in data


# ---------------------------------------------------------------------------
# /rainfall
# ---------------------------------------------------------------------------

def test_rainfall_known_city(client):
    r = client.get("/rainfall?city=kolkata")
    assert r.status_code == 200
    data = r.get_json()
    assert data["annualRainfallMm"] == 1600


def test_rainfall_unknown_city(client):
    r = client.get("/rainfall?city=unknowncity")
    assert r.status_code == 200
    data = r.get_json()
    assert data["annualRainfallMm"] > 0


# ---------------------------------------------------------------------------
# /leaderboard
# ---------------------------------------------------------------------------

def test_leaderboard(client):
    r = client.get("/leaderboard")
    assert r.status_code == 200
    data = r.get_json()
    assert "leaderboard" in data
    assert len(data["leaderboard"]) >= 1
    assert "totalLitersRecharged" in data
    assert "olympicPoolsEquivalent" in data


# ---------------------------------------------------------------------------
# /vendors
# ---------------------------------------------------------------------------

def test_vendors(client):
    r = client.get("/vendors")
    assert r.status_code == 200
    data = r.get_json()
    assert "vendors" in data
    assert len(data["vendors"]) >= 1
    vendor = data["vendors"][0]
    assert "name" in vendor
    assert "rating" in vendor
