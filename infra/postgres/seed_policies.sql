-- Zero Trust IAM — Seed Policies
-- 20 realistic RBAC + ABAC rules across 3 roles

INSERT INTO policies (name, role, resource, action, effect, allowed_hours_start, allowed_hours_end, max_risk_score) VALUES

-- ── Analyst role ──────────────────────────────────────────
('analyst-read-reports',       'analyst', 'finance-reports',   'READ',    'ALLOW', 8,  18, 40),
('analyst-read-dashboard',     'analyst', 'dashboard',         'READ',    'ALLOW', NULL, NULL, 50),
('analyst-deny-write-reports', 'analyst', 'finance-reports',   'WRITE',   'DENY',  NULL, NULL, 100),
('analyst-deny-delete-any',    'analyst', 'finance-reports',   'DELETE',  'DENY',  NULL, NULL, 100),
('analyst-deny-prod-db',       'analyst', 'prod-database',     'READ',    'DENY',  NULL, NULL, 100),
('analyst-deny-user-mgmt',     'analyst', 'user-management',   'WRITE',   'DENY',  NULL, NULL, 100),
('analyst-read-audit-logs',    'analyst', 'audit-logs',        'READ',    'ALLOW', 8,  18, 40),

-- ── Engineer role ─────────────────────────────────────────
('engineer-read-prod-db',      'engineer', 'prod-database',    'READ',    'ALLOW', 7,  20, 50),
('engineer-write-prod-db',     'engineer', 'prod-database',    'WRITE',   'ALLOW', 9,  17, 30),
('engineer-deny-delete-db',    'engineer', 'prod-database',    'DELETE',  'DENY',  NULL, NULL, 100),
('engineer-read-reports',      'engineer', 'finance-reports',  'READ',    'ALLOW', NULL, NULL, 50),
('engineer-deny-finance-write','engineer', 'finance-reports',  'WRITE',   'DENY',  NULL, NULL, 100),
('engineer-deploy-services',   'engineer', 'service-deploy',   'EXECUTE', 'ALLOW', 7,  22, 40),
('engineer-deny-user-mgmt',    'engineer', 'user-management',  'WRITE',   'DENY',  NULL, NULL, 100),

-- ── Admin role ────────────────────────────────────────────
('admin-full-prod-db',         'admin', 'prod-database',      'READ',    'ALLOW', NULL, NULL, 60),
('admin-write-prod-db',        'admin', 'prod-database',      'WRITE',   'ALLOW', NULL, NULL, 40),
('admin-delete-prod-db',       'admin', 'prod-database',      'DELETE',  'ALLOW', 9,  17, 20),
('admin-user-management',      'admin', 'user-management',    'WRITE',   'ALLOW', NULL, NULL, 30),
('admin-read-audit-logs',      'admin', 'audit-logs',         'READ',    'ALLOW', NULL, NULL, 70),
('admin-read-all-reports',     'admin', 'finance-reports',    'READ',    'ALLOW', NULL, NULL, 60);
