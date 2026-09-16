import time
import pytest
from fastapi.testclient import TestClient
from main import app
import consenses

client = TestClient(app)

# 1. API Availability & Universal Envelope Structure (Section 1.2 & 3)
def test_api_availability_and_schema():
    response = client.get("/v1/travel/risk?country=PK&region=KHI")
    assert response.status_code == 200
    
    body = response.json()
    assert "data" in body
    assert "meta" in body
    
    # Check data payload requirements
    data = body["data"]
    assert data["country"] == "PK"
    assert data["region"] == "KHI"
    assert data["risk_level"] in ["low", "medium", "high", "extreme"]
    assert isinstance(data["advisories"], list)
    assert len(data["advisories"]) > 0
    
    # Check meta envelope requirements
    meta = body["meta"]
    assert "request_id" in meta
    assert "freshness" in meta
    assert "provenance" in meta
    assert "trust" in meta
    assert meta["trust"]["confidence"] >= 0.0

# 2. SLA & Latency Profile Test: p95 < 200ms (Section 1.4)
def test_sla_latency_p95():
    latencies = []
    
    # Execute sustained polling (50 requests)
    for _ in range(50):
        start = time.perf_counter()
        resp = client.get("/v1/travel/risk?country=PK")
        elapsed_ms = (time.perf_counter() - start) * 1000
        latencies.append(elapsed_ms)
        assert resp.status_code == 200

    latencies.sort()
    p95_index = int(0.95 * len(latencies))
    p95_latency = latencies[p95_index]
    
    print(f"\n[SLA BENCHMARK] 50 Requests | p95 Latency: {p95_latency:.2f} ms")
    assert p95_latency < 200.0, f"SLA Violation: p95 was {p95_latency:.2f} ms (Target: < 200ms)"

# 3. Source Failover Test (Section 1.1 & 1.4)
def test_source_failover(monkeypatch):
    # Simulate Provider 1 (US State Dept) failing
    def broken_fetch(country):
        raise ConnectionError("Simulated upstream provider outage")

    monkeypatch.setattr(consenses, "fetch_us_state_dept", broken_fetch)

    # Execute consensus under degraded conditions
    degraded_result = consenses.compute_risk_consensus("PK")
    
    # Verification of failover behavior
    assert degraded_result["verified"] is False
    assert degraded_result["confidence"] == 0.65
    assert len(degraded_result["warnings"]) > 0
    assert "SRC-UK-FCDO" in degraded_result["sources_used"]

# 4. Storage Purge / TTL Lifecycle Test (Section 1.3)
def test_ttl_purge_endpoint():
    response = client.post("/v1/system/purge")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "purged_records" in response.json()