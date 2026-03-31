export interface AccessEvent {
  id: string
  user_id: string
  username: string | null
  user_role: string | null
  resource: string
  action: string
  decision: 'ALLOW' | 'DENY'
  deny_reason: string | null
  risk_score: number
  risk_level: string | null
  ip_address: string | null
  created_at: string
}

export interface Stats {
  total_requests: number
  allowed: number
  denied: number
  avg_risk_score: number
  deny_rate: number
}

export interface Policy {
  id: string
  name: string
  role: string
  resource: string
  action: string
  effect: 'ALLOW' | 'DENY'
  allowed_hours_start: number | null
  allowed_hours_end: number | null
  max_risk_score: number
  created_at: string
}

export interface Session {
  id: string
  user_id: string
  username: string | null
  user_role: string | null
  ip_address: string | null
  risk_score: number
  risk_level: string | null
  started_at: string
  last_active: string
  is_active: boolean
}
