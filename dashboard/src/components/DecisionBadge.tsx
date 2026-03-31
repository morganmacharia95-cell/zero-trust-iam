interface Props {
  decision: 'ALLOW' | 'DENY'
}

export function DecisionBadge({ decision }: Props) {
  return decision === 'ALLOW' ? (
    <span className="allow-badge">ALLOW</span>
  ) : (
    <span className="deny-badge">DENY</span>
  )
}

interface RiskProps {
  level: string | null
  score: number
}

export function RiskBadge({ level, score }: RiskProps) {
  const cls =
    level === 'CRITICAL' ? 'risk-critical' :
    level === 'HIGH'     ? 'risk-high'     :
    level === 'MEDIUM'   ? 'risk-medium'   :
                           'risk-low'

  return (
    <span className={`font-mono text-xs ${cls}`}>
      {score} <span className="text-zt-muted">({level ?? 'LOW'})</span>
    </span>
  )
}
