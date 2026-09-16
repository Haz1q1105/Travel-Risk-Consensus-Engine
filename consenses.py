from datetime import datetime, timezone

# 1. Map words to numbers so we can calculate a mathematical average
SEVERITY_MAP = {
    "low": 1.0,
    "medium": 2.0,
    "high": 3.0,
    "extreme": 4.0
}

REVERSE_SEVERITY_MAP = {
    1: "low",
    2: "medium",
    3: "high",
    4: "extreme"
}

# --- SOURCE 1: US Department of State Adapter ---
def fetch_us_state_dept(country_code):
    country = country_code.upper()
    sample_database = {
        "PK": {"level": "medium", "notes": "Exercise increased caution due to terrorism and localized unrest."},
        "US": {"level": "low", "notes": "Normal precautions apply."},
        "GB": {"level": "low", "notes": "Normal precautions apply."},
        "UA": {"level": "extreme", "notes": "Do not travel due to active armed conflict."},
    }
    
    record = sample_database.get(country, {"level": "medium", "notes": "Exercise increased precautions."})
    return {
        "source_id": "SRC-US-DOS",
        "publisher": "US Department of State - Consular Affairs",
        "risk_level": record["level"],
        "advisory": record["notes"],
        "retrieved_at": datetime.now(timezone.utc).isoformat()
    }

# --- SOURCE 2: UK Foreign Office (FCDO) Adapter ---
def fetch_uk_fcdo(country_code):
    country = country_code.upper()
    sample_database = {
        "PK": {"level": "medium", "notes": "FCDO advises against all travel to border areas; caution elsewhere."},
        "US": {"level": "low", "notes": "Standard safety vigilance required."},
        "GB": {"level": "low", "notes": "Standard safety vigilance required."},
        "UA": {"level": "extreme", "notes": "FCDO advises against all travel."},
    }
    
    record = sample_database.get(country, {"level": "medium", "notes": "Check regional advisories before travel."})
    return {
        "source_id": "SRC-UK-FCDO",
        "publisher": "UK Foreign, Commonwealth & Development Office",
        "risk_level": record["level"],
        "advisory": record["notes"],
        "retrieved_at": datetime.now(timezone.utc).isoformat()
    }

# --- CONSENSUS ENGINE ---
def compute_risk_consensus(country_code, region_code=None):
    sources_data = []
    errors = []

    # Try fetching from Source 1
    try:
        src1 = fetch_us_state_dept(country_code)
        sources_data.append(src1)
    except Exception as e:
        errors.append(f"Source 1 failure: {str(e)}")

    # Try fetching from Source 2
    try:
        src2 = fetch_uk_fcdo(country_code)
        sources_data.append(src2)
    except Exception as e:
        errors.append(f"Source 2 failure: {str(e)}")

    # If both fail, report an error (no silent fallbacks allowed)
    if not sources_data:
        raise RuntimeError(f"All data sources failed for country {country_code}. Errors: {errors}")

    # Failover Mode: If one fails, use the other but drop the confidence score
    if len(sources_data) == 1:
        sole_source = sources_data[0]
        return {
            "country": country_code.upper(),
            "region": region_code.upper() if region_code else None,
            "risk_level": sole_source["risk_level"],
            "advisories": [sole_source["advisory"]],
            "sources_used": [sole_source["source_id"]],
            "confidence": 0.65,
            "quality_score": 0.70,
            "verified": False,
            "provenance": sources_data,
            "warnings": errors + ["Operating on single provider failover."]
        }

    # Consensus Calculation: Calculate the numerical average of both opinions
    sev_values = [SEVERITY_MAP.get(s["risk_level"], 2.0) for s in sources_data]
    avg_severity = sum(sev_values) / len(sev_values)
    rounded_sev = int(round(avg_severity))
    final_risk = REVERSE_SEVERITY_MAP.get(rounded_sev, "medium")

    # If both sources match exactly, give high confidence
    levels_match = (sources_data[0]["risk_level"] == sources_data[1]["risk_level"])
    confidence = 0.96 if levels_match else 0.80
    quality_score = 0.98 if levels_match else 0.85

    return {
        "country": country_code.upper(),
        "region": region_code.upper() if region_code else None,
        "risk_level": final_risk,
        "advisories": [s["advisory"] for s in sources_data],
        "sources_used": [s["source_id"] for s in sources_data],
        "confidence": confidence,
        "quality_score": quality_score,
        "verified": levels_match,
        "provenance": sources_data,
        "warnings": []
    }

if __name__ == "__main__":
    result = compute_risk_consensus("PK", "KHI")
    print("\n--- CONSENSUS RESULT ---")
    print(result)