-- Zero Trust IAM — Database Schema
-- Runs automatically on first postgres container startup

-- ── Extensions ───────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ── Policies table ────────────────────────────────────────
-- Stores RBAC + ABAC rules evaluated by the policy engine
CREATE TABLE IF NOT EXISTS policies (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name        VARCHAR(100) NOT NULL,
    role        VARCHAR(50)  NOT NULL,        -- e.g. "analyst", "engineer", "admin"
    resource    VARCHAR(100) NOT NULL,        -- e.g. "finance-reports", "prod-database"
    action      VARCHAR(20)  NOT NULL,        -- READ | WRITE | DELETE | EXECUTE
    effect      VARCHAR(10)  NOT NULL CHECK (effect IN ('ALLOW', 'DENY')),
    -- ABAC conditions (optional, NULL = no restriction)
    allowed_hours_start  SMALLINT DEFAULT NULL,  -- e.g. 8  (8am)
    allowed_hours_end    SMALLINT DEFAULT NULL,  -- e.g. 18 (6pm)
    allowed_ip_range     VARCHAR(50) DEFAULT NULL, -- CIDR e.g. "192.168.1.0/24"
    max_risk_score       SMALLINT DEFAULT 60,   -- deny if risk_score exceeds this
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- ── Access events table ───────────────────────────────────
-- Immutable audit log — every authorization decision is written here
CREATE TABLE IF NOT EXISTS access_events (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         VARCHAR(100) NOT NULL,    -- Keycloak subject claim
    username        VARCHAR(100),
    user_role       VARCHAR(50),
    resource        VARCHAR(100) NOT NULL,
    action          VARCHAR(20)  NOT NULL,
    decision        VARCHAR(10)  NOT NULL CHECK (decision IN ('ALLOW', 'DENY')),
    deny_reason     VARCHAR(255),             -- populated on DENY
    risk_score      SMALLINT DEFAULT 0,
    risk_level      VARCHAR(10),              -- LOW | MEDIUM | HIGH | CRITICAL
    ip_address      VARCHAR(45),              -- supports IPv6
    user_agent      TEXT,
    geo_country     VARCHAR(50),
    geo_city        VARCHAR(100),
    token_exp       TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ── Sessions table ────────────────────────────────────────
-- Tracks active authenticated sessions for the dashboard
CREATE TABLE IF NOT EXISTS sessions (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         VARCHAR(100) NOT NULL,
    username        VARCHAR(100),
    user_role       VARCHAR(50),
    ip_address      VARCHAR(45),
    user_agent      TEXT,
    risk_score      SMALLINT DEFAULT 0,
    risk_level      VARCHAR(10),
    started_at      TIMESTAMPTZ DEFAULT NOW(),
    last_active     TIMESTAMPTZ DEFAULT NOW(),
    is_active       BOOLEAN DEFAULT TRUE
);

-- ── Indexes ───────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_events_user_id   ON access_events(user_id);
CREATE INDEX IF NOT EXISTS idx_events_decision  ON access_events(decision);
CREATE INDEX IF NOT EXISTS idx_events_created   ON access_events(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_events_resource  ON access_events(resource);
CREATE INDEX IF NOT EXISTS idx_policies_role    ON policies(role);
CREATE INDEX IF NOT EXISTS idx_sessions_user    ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_active  ON sessions(is_active);
