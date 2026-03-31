import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
} from 'recharts'
import { Stats, AccessEvent } from '../types'

interface DonutProps { stats: Stats }

const COLORS = { ALLOW: '#1d9e75', DENY: '#ef4444' }

export function DecisionDonut({ stats }: DonutProps) {
  const data = [
    { name: 'Allow', value: stats.allowed },
    { name: 'Deny',  value: stats.denied  },
  ]
  return (
    <div className="bg-zt-surface border border-zt-border rounded-lg p-4">
      <h2 className="text-sm font-medium text-zt-text mb-4">Decision breakdown</h2>
      <ResponsiveContainer width="100%" height={200}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={55}
            outerRadius={80}
            paddingAngle={3}
            dataKey="value"
          >
            <Cell fill={COLORS.ALLOW} />
            <Cell fill={COLORS.DENY}  />
          </Pie>
          <Tooltip
            contentStyle={{ background: '#1a1d27', border: '1px solid #2a2d3a', borderRadius: 6, fontSize: 12 }}
            labelStyle={{ color: '#e2e8f0' }}
          />
        </PieChart>
      </ResponsiveContainer>
      <div className="flex justify-center gap-6 mt-2">
        <span className="text-xs text-zt-green flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-zt-teal inline-block" /> Allow
        </span>
        <span className="text-xs text-red-400 flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-red-500 inline-block" /> Deny
        </span>
      </div>
    </div>
  )
}

interface BarProps { events: AccessEvent[] }

export function RiskScoreBar({ events }: BarProps) {
  const buckets: Record<string, number> = { LOW: 0, MEDIUM: 0, HIGH: 0, CRITICAL: 0 }
  events.forEach((e) => {
    const k = e.risk_level ?? 'LOW'
    buckets[k] = (buckets[k] ?? 0) + 1
  })
  const data = Object.entries(buckets).map(([level, count]) => ({ level, count }))
  const barColors: Record<string, string> = {
    LOW: '#1d9e75', MEDIUM: '#f59e0b', HIGH: '#f97316', CRITICAL: '#ef4444',
  }

  return (
    <div className="bg-zt-surface border border-zt-border rounded-lg p-4">
      <h2 className="text-sm font-medium text-zt-text mb-4">Risk level distribution</h2>
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={data} margin={{ top: 0, right: 10, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2d3a" />
          <XAxis dataKey="level" tick={{ fill: '#6b7280', fontSize: 11 }} />
          <YAxis tick={{ fill: '#6b7280', fontSize: 11 }} />
          <Tooltip
            contentStyle={{ background: '#1a1d27', border: '1px solid #2a2d3a', borderRadius: 6, fontSize: 12 }}
          />
          <Bar dataKey="count" radius={[4, 4, 0, 0]}>
            {data.map((entry) => (
              <Cell key={entry.level} fill={barColors[entry.level] ?? '#6b7280'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
