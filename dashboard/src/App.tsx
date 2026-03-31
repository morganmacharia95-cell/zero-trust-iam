import { useCallback } from 'react'
import { usePolling } from './hooks/usePolling'
import { fetchEvents, fetchStats, fetchPolicies } from './api/client'
import { StatCards } from './components/StatCards'
import { AccessEventLog } from './components/AccessEventLog'
import { DecisionDonut, RiskScoreBar } from './components/RiskScoreChart'
import { PolicyTable } from './components/PolicyTable'
import { AccessEvent, Stats, Policy } from './types'

const EMPTY_STATS: Stats = {
  total_requests: 0, allowed: 0, denied: 0,
  avg_risk_score: 0, deny_rate: 0,
}

export default function App() {
  const {
    data: events, loading: eventsLoading,
  } = usePolling<AccessEvent[]>(useCallback(() => fetchEvents(100), []), 5000)

  const {
    data: stats,
  } = usePolling<Stats>(useCallback(() => fetchStats(), []), 5000)

  const {
    data: policies, loading: policiesLoading,
  } = usePolling<Policy[]>(useCallback(() => fetchPolicies(), []), 30000)

  const resolvedStats  = stats   ?? EMPTY_STATS
  const resolvedEvents = events  ?? []
  const resolvedPolicies = policies ?? []

  return (
    <div className="min-h-screen bg-zt-bg text-zt-text">
      {/* ── Header ── */}
      <header className="border-b border-zt-border bg-zt-surface/80 backdrop-blur sticky top-0 z-10">
        <div className="max-w-screen-xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-7 h-7 rounded bg-zt-purple/20 border border-zt-purple/40 flex items-center justify-center">
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <path d="M7 1L2 3.5V7c0 2.8 2.1 5.4 5 6 2.9-.6 5-3.2 5-6V3.5L7 1z"
                  stroke="#7c6fef" strokeWidth="1.2" strokeLinejoin="round"/>
              </svg>
            </div>
            <div>
              <h1 className="text-sm font-medium text-zt-text">Zero Trust IAM</h1>
              <p className="text-xs text-zt-muted">Policy Engine Dashboard</p>
            </div>
          </div>
          <div className="flex items-center gap-2 text-xs text-zt-muted">
            <span className="live-dot w-2 h-2 rounded-full bg-zt-teal inline-block" />
            Live · refreshes every 5s
          </div>
        </div>
      </header>

      {/* ── Main ── */}
      <main className="max-w-screen-xl mx-auto px-4 py-6 space-y-6">

        {/* Stat cards */}
        <StatCards stats={resolvedStats} />

        {/* Charts row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <DecisionDonut stats={resolvedStats} />
          <RiskScoreBar  events={resolvedEvents} />
        </div>

        {/* Live event log */}
        <AccessEventLog events={resolvedEvents} loading={eventsLoading} />

        {/* Policy table */}
        {!policiesLoading && resolvedPolicies.length > 0 && (
          <PolicyTable policies={resolvedPolicies} />
        )}
      </main>

      {/* ── Footer ── */}
      <footer className="border-t border-zt-border mt-8 py-4 text-center text-xs text-zt-muted">
        Zero Trust IAM Simulator · Policy Engine v0.1.0 ·{' '}
        <a
          href="http://localhost:8000/docs"
          target="_blank"
          rel="noreferrer"
          className="text-zt-purple hover:underline"
        >
          API docs
        </a>
      </footer>
    </div>
  )
}
