import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
})

export const fetchEvents = async (limit = 50, decision?: string) => {
  const params: Record<string, string | number> = { limit }
  if (decision) params.decision = decision
  const res = await api.get('/api/events', { params })
  return res.data
}

export const fetchStats = async () => {
  const res = await api.get('/api/events/stats')
  return res.data
}

export const fetchPolicies = async (role?: string) => {
  const params: Record<string, string> = {}
  if (role) params.role = role
  const res = await api.get('/api/policies', { params })
  return res.data
}

export const fetchSessions = async () => {
  const res = await api.get('/api/sessions')
  return res.data
}
