-- PostgreSQL Production Schema (Section 1.3 Requirement)

CREATE TABLE IF NOT EXISTS travel_risk_audit (
    id SERIAL PRIMARY KEY,
    country VARCHAR(10) NOT NULL,
    region VARCHAR(10),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    payload JSONB NOT NULL
);

-- JSONB GIN index for high-performance sub-document queries
CREATE INDEX IF NOT EXISTS idx_travel_risk_payload ON travel_risk_audit USING gin (payload);

-- B-Tree indexes for fast TTL expiration lookups and filtering
CREATE INDEX IF NOT EXISTS idx_travel_risk_country ON travel_risk_audit (country);
CREATE INDEX IF NOT EXISTS idx_travel_risk_expires_at ON travel_risk_audit (expires_at);

-- Automated TTL Purge Function
CREATE OR REPLACE FUNCTION purge_expired_advisories() 
RETURNS integer AS $$
DECLARE
    deleted_rows integer;
BEGIN
    DELETE FROM travel_risk_audit
    WHERE expires_at < NOW();
    GET DIAGNOSTICS deleted_rows = ROW_COUNT;
    RETURN deleted_rows;
END;
$$ LANGUAGE plpgsql;