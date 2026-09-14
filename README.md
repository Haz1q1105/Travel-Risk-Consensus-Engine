# Destination Risk Advisory API

A backend data pipeline and REST API that provides travel risk intelligence for autonomous agents[cite: 1]. The system ingests safety advisories from multiple providers, verifies them through consensus, tracks data freshness with TTL in PostgreSQL, and serves standardized payloads[cite: 1].

---

## What It Does

* **Fetches from Multiple Sources**: Gathers travel advisory feeds from distinct geopolitical sources without silent failures[cite: 1].
* **Consensus Verification**: Compares reported risk levels across sources to derive a single verified rating and calculate a confidence score[cite: 1].
* **Standardized JSON Envelope**: Delivers responses partitioned strictly into `"data"` and `"meta"` fields per the assignment specification[cite: 1].
* **PostgreSQL Storage & TTL**: Saves raw ingest data and audit trails in indexed JSONB columns with automated purging of expired records[cite: 1].
* **SLA Compliance**: Built to maintain $p95$ response latency below 200 ms and handle single-source failovers seamlessly[cite: 1].

---

## API Reference

### `GET /v1/travel/risk`

Retrieves the consolidated travel risk advisory for a given country and optional region[cite: 1].

#### Parameters
* `country` (required): ISO-2 country code (e.g., `PK`, `US`, `GB`)[cite: 1].
* `region` (optional): Sub-national code or city identifier (e.g., `KHI`, `LHE`)[cite: 1].

#### Response Example
```json
{
  "data": {
    "country": "PK",
    "region": "KHI",
    "risk_level": "medium",
    "advisories": [
      "Exercise increased caution due to localized civil unrest.",
      "Avoid non-essential travel to border zones."
    ],
    "issued_at": "2026-09-14",
    "sources_used": [
      "SRC-US",
      "SRC-UK"
    ]
  },
  "meta": {
    "request_id": "req_01J8FX7K3M2Q",
    "product_id": "travel.risk.advisory.v1",
    "version": "1.0.0",
    "served_at": "2026-09-14T10:00:02Z",
    "source_last_updated_at": "2026-09-14T09:55:00Z",
    "freshness": {
      "age_seconds": 300,
      "ttl_seconds": 86400,
      "stale": false
    },
    "provenance": [
      {
        "source_id": "SRC-US",
        "publisher": "US Department of State",
        "retrieved_at": "2026-09-14T09:55:00Z"
      },
      {
        "source_id": "SRC-UK",
        "publisher": "UK Foreign Office",
        "retrieved_at": "2026-09-14T09:55:00Z"
      }
    ],
    "trust": {
      "confidence": 0.96,
      "quality_score": 0.98,
      "verified": true
    },
    "license": {
      "type": "open_data",
      "usage": "agent_runtime"
    },
    "api": {
      "latency_ms": 14,
      "rate_limit": {
        "limit": 100,
        "window_seconds": 60
      }
    },
    "warnings": []
  }
}
