import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, Tooltip,
  CartesianGrid, ResponsiveContainer, Legend
} from 'recharts'
import { useState } from 'react'

const METRICS = [
  { key: 'likes',          label: 'Likes',    color: '#FF9933' },
  { key: 'comments_count', label: 'Comments', color: '#CC5200' },
  { key: 'saves',          label: 'Saves',    color: '#F5A030' },
  { key: 'shares',         label: 'Shares',   color: '#1A0E04' },
]

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div style={{
      background: 'var(--surface)', border: '1px solid var(--rule)',
      borderRadius: 'var(--r-md)', padding: '12px 16px', fontSize: 12,
      boxShadow: 'var(--shadow-float)',
    }}>
      <p style={{ fontFamily: 'var(--font-data)', color: 'var(--ink-3)', marginBottom: 8, fontSize: 10, letterSpacing: '0.06em' }}>{label}</p>
      {payload.map(p => (
        <div key={p.name} style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 4 }}>
          <div style={{ width: 7, height: 7, borderRadius: '50%', background: p.color, flexShrink: 0 }} />
          <span style={{ color: 'var(--ink-3)', fontFamily: 'var(--font-data)', fontSize: 11 }}>{p.name}:</span>
          <span style={{ color: 'var(--ink-1)', fontFamily: 'var(--font-data)', fontWeight: 500, fontSize: 12 }}>
            {Number(p.value).toLocaleString()}
          </span>
        </div>
      ))}
    </div>
  )
}

export default function EngagementChart({ posts, hideTitle = false }) {
  const [view, setView] = useState('area')

  if (!posts?.length) return null

  const data = [...posts]
    .sort((a, b) => new Date(a.posted_at) - new Date(b.posted_at))
    .map((p, i) => ({
      name: `Post ${i + 1}`,
      type: p.is_collaboration ? 'collab' : 'personal',
      likes: p.likes,
      comments_count: p.comments_count,
      saves: p.saves,
      shares: p.shares,
    }))

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: hideTitle ? 'flex-end' : 'space-between', marginBottom: 16, flexWrap: 'wrap', gap: 12 }}>
        {!hideTitle && <p className="section-title" style={{ margin: 0 }}>Engagement Per Post</p>}
        <div style={{ display: 'flex', gap: 8 }}>
          {['area', 'bar'].map(v => (
            <button key={v} className={`btn ${view === v ? 'btn-primary' : 'btn-ghost'}`}
              style={{ padding: '6px 14px', fontSize: 12, borderRadius: 'var(--radius-sm)' }}
              onClick={() => setView(v)}>
              {v === 'area' ? 'Area' : 'Bar'}
            </button>
          ))}
        </div>
      </div>

      <div style={{ background: 'var(--surface)', border: '1px solid var(--rule)', borderRadius: 'var(--r-lg)', padding: '24px 8px 8px', boxShadow: 'var(--shadow-card)' }}>
        <ResponsiveContainer width="100%" height={280}>
          {view === 'area' ? (
            <AreaChart data={data} margin={{ left: 0, right: 20, top: 10, bottom: 0 }}>
              <defs>
                {METRICS.map(m => (
                  <linearGradient key={m.key} id={`grad-${m.key}`} x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={m.color} stopOpacity={0.3} />
                    <stop offset="95%" stopColor={m.color} stopOpacity={0} />
                  </linearGradient>
                ))}
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.05)" />
              <XAxis dataKey="name" tick={{ fill: '#8892aa', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#8892aa', fontSize: 11 }} axisLine={false} tickLine={false}
                tickFormatter={v => v >= 1000 ? `${(v/1000).toFixed(0)}K` : v} width={48} />
              <Tooltip content={<CustomTooltip />} />
              <Legend iconType="circle" iconSize={8}
                wrapperStyle={{ fontSize: 12, color: 'var(--text-secondary)', paddingTop: 12 }} />
              {METRICS.map(m => (
                <Area key={m.key} type="monotone" dataKey={m.key} name={m.label}
                  stroke={m.color} strokeWidth={2} fill={`url(#grad-${m.key})`} dot={false} />
              ))}
            </AreaChart>
          ) : (
            <BarChart data={data} margin={{ left: 0, right: 20, top: 10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.05)" />
              <XAxis dataKey="name" tick={{ fill: '#8892aa', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#8892aa', fontSize: 11 }} axisLine={false} tickLine={false}
                tickFormatter={v => v >= 1000 ? `${(v/1000).toFixed(0)}K` : v} width={48} />
              <Tooltip content={<CustomTooltip />} />
              <Legend iconType="circle" iconSize={8}
                wrapperStyle={{ fontSize: 12, color: 'var(--text-secondary)', paddingTop: 12 }} />
              {METRICS.map(m => (
                <Bar key={m.key} dataKey={m.key} name={m.label} fill={m.color} radius={[3, 3, 0, 0]} maxBarSize={18} />
              ))}
            </BarChart>
          )}
        </ResponsiveContainer>

        {/* Collab post indicators */}
        <div style={{ display: 'flex', gap: 16, padding: '12px 16px 0', flexWrap: 'wrap' }}>
          {data.map((d, i) => d.type === 'collab' && (
            <span key={i} className="badge badge-amber" style={{ fontSize: 10 }}>
              Post {i + 1}: Collab
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}
