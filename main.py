import time
import uuid
from datetime import datetime, timezone
from fastapi import FastAPI

# Create the API
app = FastAPI(
    title="Travel Risk API",
    description="Allowing autonomous AI agents to find security risks in countries and regions")

# initializing the app
@app.get("/v1/travel/risk")
def get_travel_risk(country: str = "PK", region: str = "KHI"):
    start_time = time.perf_counter()

    # 1. The actual answer (What is the risk?)
    data_answer = {
        "country": country,
        "region": region,
        "risk_level": "medium",
        "advisories": [
            "Exercise increased caution due to localized civil unrest.",
            "Avoid non-essential travel to border zones."
        ],
        "issued_at": "2026-09-14",
        "sources_used": ["US-State-Dept", "UK-FCDO"]
    }

    # Measure how many milliseconds it took to answer
    latency_ms = int((time.perf_counter() - start_time) * 1000)

    # 2. The metadata envelope (The requirements from the assignment PDF)
    meta_info = {
        "request_id": f"req_{uuid.uuid4().hex[:12]}",
        "product_id": "travel.risk.advisory.v1",
        "version": "1.0.0",
        "served_at": datetime.now(timezone.utc).isoformat(),
        "source_last_updated_at": datetime.now(timezone.utc).isoformat(),
        "freshness": {
            "age_seconds": 120,
            "ttl_seconds": 86400,
            "stale": False
        },
        "provenance": [
            {"source_id": "SRC-US", "publisher": "US State Dept", "retrieved_at": "2026-09-14T10:00:00Z"},
            {"source_id": "SRC-UK", "publisher": "UK FCDO", "retrieved_at": "2026-09-14T10:00:00Z"}
        ],
        "trust": {
            "confidence": 0.95,
            "quality_score": 0.98,
            "verified": True
        },
        "license": {
            "type": "open_data",
            "usage": "agent_runtime"
        },
        "api": {
            "latency_ms": latency_ms,
            "rate_limit": {"limit": 100, "window_seconds": 60}
        },
        "warnings": []
    }

    # Return both together in one JSON object
    return {
        "data": data_answer,
        "meta": meta_info
    }