# API Reference

Base URL: `http://localhost:5000`

---

## POST /calculate

Calculate annual runoff and harvested water potential.

**Request body (JSON)**

| Field                | Type    | Required | Description                                   |
|----------------------|---------|----------|-----------------------------------------------|
| roofArea / roof_area | number  | Yes      | Roof area in m² (camelCase or snake_case)     |
| location             | string  | Yes      | City or location name                         |
| dwellers             | integer | No       | Number of household members (default: 4)      |
| rainfall             | number  | No       | Annual rainfall in mm (derived if omitted)    |

> **Validation:** `roofArea` must be > 0; returns HTTP 400 otherwise.

**Response (JSON)**

```json
{
  "annualRainfallMm": 1600,
  "runoffLiters": 140800,
  "harvestedWaterLiters": 140800,
  "waterDemandLiters": 219000,
  "feasible": true,
  "runoffCoefficient": 0.8,
  "aquifer": "Alluvium (sand & gravel)",
  "groundwaterDepth": "12-18 m below ground level",
  "policy": "25% subsidy on recharge pits under state groundwater conservation scheme."
}
```

---

## POST /recommend

Recommend a recharge structure based on open space and runoff volume.

**Request body (JSON)**

| Field                   | Type   | Required | Description                                               |
|-------------------------|--------|----------|-----------------------------------------------------------|
| openSpace / open_space  | number | No*      | Available open space in m²                                |
| roofArea / roof_area    | number | No*      | Roof area in m² — open space estimated as 25% if openSpace absent |
| runoff                  | number | No       | Annual runoff in litres (default: 50000)                  |

> \* At least one of `openSpace` or `roofArea` should be supplied. If neither is provided, open space defaults to 10 m².
> **Validation:** `openSpace` must be ≥ 0; returns HTTP 400 otherwise.

**Response (JSON)**

```json
{
  "structure": "Recharge pit",
  "dimensions": "2.1 m × 2.1 m × 2.0 m",
  "rechargeVolumeM3": 9.0
}
```

Structure selection logic:
- `openSpace >= 25 m²` → Recharge pit
- `12 m² ≤ openSpace < 25 m²` → Recharge trench
- `openSpace < 12 m²` → Recharge shaft

---

## POST /cost

Estimate installation cost and cost-benefit analysis.

**Request body (JSON)**

| Field            | Type   | Required | Description                                                          |
|------------------|--------|----------|----------------------------------------------------------------------|
| structure / type | string | No       | Full name or short alias (see table below). Default: "Recharge pit"  |
| runoff           | number | No       | Annual runoff in litres (default: 50000)                             |

**Short-name aliases for `type`**

| Alias     | Resolves to      |
|-----------|------------------|
| `pit`     | Recharge pit     |
| `trench`  | Recharge trench  |
| `shaft`   | Recharge shaft   |
| `tank`    | Storage tank     |

**Response (JSON)**

```json
{
  "structure": "Recharge pit",
  "costRs": 5000,
  "annualSavingsRs": 7040,
  "paybackYears": 0.7,
  "environmentalBenefitLiters": 140800,
  "carbonOffsetKg": 28
}
```

Cost schedule (CGWB estimates):

| Structure      | Cost (₹) |
|----------------|----------|
| Recharge pit   | 5,000    |
| Recharge trench| 7,000    |
| Recharge shaft | 7,000    |
| Storage tank   | 10,000   |

---

## GET /rainfall

Retrieve annual rainfall data for a city.

**Query parameters**

| Param | Type   | Description          |
|-------|--------|----------------------|
| city  | string | City or location name |

**Example**

```
GET /rainfall?city=Kolkata
```

**Response (JSON)**

```json
{
  "city": "Kolkata",
  "annualRainfallMm": 1600,
  "source": "CGWB Mock Data"
}
```

---

## GET /leaderboard

Return the community water credit leaderboard.

**Response (JSON)**

```json
{
  "leaderboard": [
    {
      "rank": 1,
      "name": "Green Valley Society",
      "city": "Pune",
      "credits": 4200,
      "litersRecharged": 420000
    }
  ],
  "totalLitersRecharged": 1760000,
  "olympicPoolsEquivalent": 0.7
}
```

---

## GET /vendors

Return a list of marketplace vendors.

**Response (JSON)**

```json
{
  "vendors": [
    { "name": "RainCharge Solutions", "rating": 4.8, "city": "Pan-India" }
  ]
}
```
