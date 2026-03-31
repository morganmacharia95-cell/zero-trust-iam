import { AccessEvent } from '../types'
import { DecisionBadge, RiskBadge } from './DecisionBadge'

interface Props {
  events: AccessEvent[]
  loading: boolean
}

function timeAgo(iso: string) {
  const diff = Math.floor((Date.now() - new Date(iso).getTime()) / 1000)
  if (diff < 60)  return `${diff}s ago`
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
  return `${Math.floor(diff / 3600)}h ago`
}

export function AccessEventLog({ events, loading }: Props) {
  return (
    <div className="bg-zt-surface border border-zt-border rounded-lg overflow-hidden">
      <div className="flex items-center justify-between px-4 py-3 border-b border-zt-border">
        <h2 className="text-sm font-medium text-zt-text">Access event log</h2>
        <div className="flex items-center gap-2">
          <span className="live-dot w-2 h-2 rounded-full bg-zt-teal inline-block" />
          <span className="text-xs text-zt-muted">live</span>
        </div>
      </div>

      {loading ? (
        <div className="p-8 text-center text-zt-muted text-sm">Loading events...</div>
      ) : events.length === 0 ? (
        <div className="p-8 text-center text-zt-muted text-sm">
          No events yet — make an authorization request to see data here
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="text-zt-muted border-b border-zt-border">
                <th className="text-left px-4 py-2 font-medium">Time</th>
                <th className="text-left px-4 py-2 font-medium">User</th>
                <th className="text-left px-4 py-2 font-medium">Role</th>
                <th className="text-left px-4 py-2 font-medium">Resource</th>
                <th className="text-left px-4 py-2 font-medium">Action</th>
                <th className="text-left px-4 py-2 font-medium">Decision</th>
                <th className="text-left px-4 py-2 font-medium">Risk</th>
                <th className="text-left px-4 py-2 font-medium">Reason</th>
              </tr>
            </thead>
            <tbody>
              {events.map((e) => (
                <tr
                  key={e.id}
                  className="border-b border-zt-border/50 hover:bg-zt-border/20 transition-colors"
                >
                  <td className="px-4 py-2.5 text-zt-muted font-mono whitespace-nowrap">
                    {timeAgo(e.created_at)}
                  </td>
                  <td className="px-4 py-2.5 text-zt-text font-mono">
                    {e.username ?? e.user_id.slice(0, 8)}
                  </td>
                  <td className="px-4 py-2.5">
                    <span className="text-zt-purple">{e.user_role ?? '—'}</span>
                  </td>
                  <td className="px-4 py-2.5 text-zt-text font-mono">
                    {e.resource}
                  </td>
                  <td className="px-4 py-2.5 text-zt-muted">{e.action}</td>
                  <td className="px-4 py-2.5">
                    <DecisionBadge decision={e.decision} />
                  </td>
                  <td className="px-4 py-2.5">
                    <RiskBadge level={e.risk_level} score={e.risk_score} />
                  </td>
                  <td className="px-4 py-2.5 text-zt-muted max-w-xs truncate">
                    {e.deny_reason ?? '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
