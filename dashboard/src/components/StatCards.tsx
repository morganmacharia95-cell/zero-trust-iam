import { Stats } from '../types'

interface Props { stats: Stats }

export function StatCards({ stats }: Props) {
  const cards = [
    {
      label: 'Total requests',
      value: stats.total_requests.toLocaleString(),
      color: 'text-zt-purple',
      bg: 'border-zt-purple/30',
    },
    {
      label: 'Allowed',
      value: stats.allowed.toLocaleString(),
      color: 'text-zt-green',
      bg: 'border-zt-teal/30',
    },
    {
      label: 'Denied',
      value: stats.denied.toLocaleString(),
      color: 'text-red-400',
      bg: 'border-red-800/30',
    },
    {
      label: 'Deny rate',
      value: `${stats.deny_rate.toFixed(1)}%`,
      color: stats.deny_rate > 50 ? 'text-red-400' : 'text-zt-amber',
      bg: 'border-zt-amber/30',
    },
    {
      label: 'Avg risk score',
      value: stats.avg_risk_score.toFixed(1),
      color: stats.avg_risk_score > 60 ? 'text-red-400' : 'text-zt-teal',
      bg: 'border-zt-teal/30',
    },
  ]

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 mb-6">
      {cards.map((c) => (
        <div
          key={c.label}
          className={`bg-zt-surface border ${c.bg} rounded-lg p-4`}
        >
          <p className="text-zt-muted text-xs uppercase tracking-widest mb-1">
            {c.label}
          </p>
          <p className={`text-2xl font-medium ${c.color}`}>{c.value}</p>
        </div>
      ))}
    </div>
  )
}
