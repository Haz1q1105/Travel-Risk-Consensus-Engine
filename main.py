import time
import uuid
from datetime import datetime, timezone
from fastapi import FastAPI, Query, HTTPException
from consenses import compute_risk_consensus

app = FastAPI(
    title="Destination Risk Advisory API",
    version="1.0.0",
    description="Consensus-driven travel safety intelligence for autonomous agents."
)

@app.get("/v1/travel/risk")
def get_travel_risk(
    country: str = Query(..., min_length=2, max_length=2, description="ISO-2 Country code, e.g. PK, US, UA"),
    region: str = Query(None, description="Regional sub-code, e.g. KHI, LHE")
):
    start_time = time.perf_counter()
    country_code = country.upper()
    region_code = region.upper() if region else None

    # 1. Execute consensus verification across providers
    try:
        consensus_result = compute_risk_consensus(country_code, region_code)
    except Exception as e:
        # Propagate upstream system errors explicitly (Section 1.1)
        raise HTTPException(status_code=502, detail=f"Upstream provider failure: {str(e)}")

    # 2. Build the primary data payload required by the catalog
    data_payload = {
        "country": consensus_result["country"],
        "region": consensus_result["region"],
        "risk_level": consensus_result["risk_level"],
        "advisories": consensus_result["advisories"],
        "issued_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "sources_used": consensus_result["sources_used"]
    }

    # 3. Calculate latency in milliseconds (< 200 ms target)
    latency_ms = int((time.perf_counter() - start_time) * 1000)

    # 4. Wrap with the Universal Response Envelope (Section 3)
    meta_payload = {
        "request_id": f"req_{uuid.uuid4().hex[:16]}",
        "product_id": "travel.risk.advisory.v1",
        "version": "1.0.0",
        "served_at": datetime.now(timezone.utc).isoformat(),
        "source_last_updated_at": consensus_result["provenance"][0]["retrieved_at"],
        "freshness": {
            "age_seconds": 0,
            "ttl_seconds": 86400,
            "stale": False
        },
        "provenance": consensus_result["provenance"],
        "trust": {
            "confidence": consensus_result["confidence"],
            "quality_score": consensus_result["quality_score"],
            "verified": consensus_result["verified"]
        },
        "license": {
            "type": "open_data",
            "usage": "agent_runtime"
        },
        "api": {
            "latency_ms": latency_ms,
            "rate_limit": {
                "limit": 100,
                "window_seconds": 60
            }
        },
        "warnings": consensus_result["warnings"]
    }

    return {
        "data": data_payload,
        "meta": meta_payload
    }