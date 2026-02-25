# Test Report — Rainwater Harvesting Smart Assessment System

**Date:** 2026-02-25  
**Tester:** Copilot QA Agent  
**Backend:** Flask 2.x · `http://127.0.0.1:5000`  
**Frontend:** Static HTML/CSS/JS served from `frontend/`

---

## Step 2 — Backend API Tests

### Test 1 · POST /calculate

| Field        | Value |
|--------------|-------|
| **Input**    | `{"roof_area": 100, "location": "Kolkata"}` |
| **Expected** | `harvestedWaterLiters > 0` |
| **Result**   | `harvestedWaterLiters: 128000` |
| **Status**   | ✅ PASS |

**Notes:** Kolkata annual rainfall = 1600 mm.  
Formula: `100 m² × 1600 mm × 0.8 = 128,000 L` ✔

---

### Test 2 · POST /recommend

| Field        | Value |
|--------------|-------|
| **Input**    | `{"roof_area": 100}` |
| **Expected** | One of: Recharge Pit / Trench / Shaft / Tank |
| **Result**   | `structure: "Recharge pit"` |
| **Status**   | ✅ PASS |

**Notes:** `roof_area = 100` → estimated open space = 25 m² (25% of roof area) → `openSpace ≥ 25` → Recharge pit.

---

### Test 3 · POST /cost

| Field        | Value |
|--------------|-------|
| **Input**    | `{"type": "pit"}` |
| **Expected** | `costRs: 5000` |
| **Result**   | `costRs: 5000` |
| **Status**   | ✅ PASS |

**Notes:** Short alias `"pit"` resolved to full name `"Recharge pit"`. CGWB cost schedule: Recharge pit = ₹5,000.

---

### Additional Endpoint Tests

| Endpoint          | Method | Status | Notes |
|-------------------|--------|--------|-------|
| `GET /rainfall`   | GET    | ✅ PASS | `?city=Kolkata` → 1600 mm |
| `GET /leaderboard`| GET    | ✅ PASS | Returns 5 community entries |
| `GET /vendors`    | GET    | ✅ PASS | Returns 5 vendor records |

---

## Step 5 — Edge Case Tests

| Test | Input | Expected | Result | Status |
|------|-------|----------|--------|--------|
| EC-1 | `roofArea: 0` | 400 error | `{"error": "roofArea must be greater than 0"}` | ✅ PASS |
| EC-2 | `roofArea: -50` | 400 error | `{"error": "roofArea must be greater than 0"}` | ✅ PASS |
| EC-3 | `openSpace: -5` | 400 error | `{"error": "openSpace must be 0 or greater"}` | ✅ PASS |
| EC-4 | `{}` (empty body) | defaults used | Returns 200 with sensible defaults | ✅ PASS |
| EC-5 | `{"type": "tank"}` | `costRs: 10000` | `costRs: 10000` | ✅ PASS |

---

## Step 4 — Integration Test (Frontend ↔ Backend)

| Check | Result |
|-------|--------|
| CORS headers present | ✅ `flask-cors` applied globally |
| API base URL in JS | ✅ `http://localhost:5000` |
| Frontend falls back gracefully when API is offline | ✅ Local calculations used |

---

## Step 7 — Validation

| Check | Formula / Logic | Result |
|-------|-----------------|--------|
| Calculation formula | `roofArea × rainfall_mm × 0.8` | ✅ Correct (CGWB standard) |
| Recommendation logic | openSpace ≥ 25 → pit; ≥ 12 → trench; < 12 → shaft | ✅ Correct |
| Cost values | Pit=5000, Trench=7000, Shaft=7000, Tank=10000 | ✅ Matches CGWB estimates |
| Water demand | `dwellers × 150 L/day × 365` | ✅ Correct |

---

## Summary

| Category | Tests | Pass | Fail |
|----------|-------|------|------|
| Backend API | 6 | 6 | 0 |
| Edge Cases | 5 | 5 | 0 |
| Integration | 3 | 3 | 0 |
| Validation | 4 | 4 | 0 |
| **Total** | **18** | **18** | **0** |

**All tests passed after applying the fixes documented in `bug_report.md`.**

---

## Screenshots

| File | Description |
|------|-------------|
| `screenshots/home_screen.png` | Frontend home screen with Quick Assessment form |
| `screenshots/backend_test_1.png` | API tests 1-3 request/response pairs |
| `screenshots/backend_test_2.png` | Edge case tests EC-1 through EC-5 |
