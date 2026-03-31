import { Policy } from '../types'

interface Props { policies: Policy[] }

export function PolicyTable({ policies }: Props) {
  return (
    <div className="bg-zt-surface border border-zt-border rounded-lg overflow-hidden">
      <div className="px-4 py-3 border-b border-zt-border">
        <h2 className="text-sm font-medium text-zt-text">Active policies</h2>
        <p className="text-xs text-zt-muted mt-0.5">{policies.length} rules loaded</p>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="text-zt-muted border-b border-zt-border">
              <th className="text-left px-4 py-2 font-medium">Role</th>
              <th className="text-left px-4 py-2 font-medium">Resource</th>
              <th className="text-left px-4 py-2 font-medium">Action</th>
              <th className="text-left px-4 py-2 font-medium">Effect</th>
              <th className="text-left px-4 py-2 font-medium">Hours (UTC)</th>
              <th className="text-left px-4 py-2 font-medium">Max risk</th>
            </tr>
          </thead>
          <tbody>
            {policies.map((p) => (
              <tr key={p.id} className="border-b border-zt-border/50 hover:bg-zt-border/20">
                <td className="px-4 py-2.5 text-zt-purple font-mono">{p.role}</td>
                <td className="px-4 py-2.5 text-zt-text font-mono">{p.resource}</td>
                <td className="px-4 py-2.5 text-zt-muted">{p.action}</td>
                <td className="px-4 py-2.5">
                  {p.effect === 'ALLOW' ? (
                    <span className="allow-badge">ALLOW</span>
                  ) : (
                    <span className="deny-badge">DENY</span>
                  )}
                </td>
                <td className="px-4 py-2.5 text-zt-muted font-mono">
                  {p.allowed_hours_start != null
                    ? `${p.allowed_hours_start}:00 – ${p.allowed_hours_end}:00`
                    : 'Any time'}
                </td>
                <td className="px-4 py-2.5">
                  <span className={p.max_risk_score < 40 ? 'risk-high' : 'risk-low'}>
                    {p.max_risk_score}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
