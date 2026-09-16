import json
import sqlite3
from datetime import datetime, timezone, timedelta

DB_FILE = "travel_risk.db"

def init_db():
    """Initializes local storage table."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS travel_risk_audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country TEXT NOT NULL,
            region TEXT,
            created_at TIMESTAMP NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            payload TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_advisory_record(country: str, region: str, payload_dict: dict, ttl_seconds: int = 86400):
    """
    Saves the payload with a Time-To-Live (TTL) expiration.
    Default TTL: 86400 seconds (24 hours).
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    now = datetime.now(timezone.utc)
    expires = now + timedelta(seconds=ttl_seconds)
    
    cursor.execute("""
        INSERT INTO travel_risk_audit (country, region, created_at, expires_at, payload)
        VALUES (?, ?, ?, ?, ?)
    """, (
        country.upper(),
        region.upper() if region else None,
        now.isoformat(),
        expires.isoformat(),
        json.dumps(payload_dict)
    ))
    conn.commit()
    conn.close()

def purge_expired_records():
    """
    Automated TTL Purge: deletes records where expires_at < now.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    now_iso = datetime.now(timezone.utc).isoformat()
    cursor.execute("DELETE FROM travel_risk_audit WHERE expires_at < ?", (now_iso,))
    deleted_count = cursor.rowcount
    
    conn.commit()
    conn.close()
    return deleted_count