import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'

function ConfidenceBadge({ level }) {
  const color = level === 'High' ? 'var(--accent-secondary)' : level === 'Medium' ? 'var(--accent-amber)' : 'var(--text-muted)'
  return (
    <span style={{ fontSize: 11, fontWeight: 700, color, padding: '2px 8px',
      background: `${color}18`, borderRadius: 'var(--radius-full)', border: `1px solid ${color}30` }}>
      {level} confidence
    </span>
  )
}

function GenderBar({ female, male, unknown }) {
  const segments = [
    { label: 'Female', pct: female, color: '#ff6b9d' },
    { label: 'Male', pct: male, color: '#6c63ff' },
    { label: 'Unknown', pct: unknown, color: '#4a5168' },
  ]
  return (
    <div>
      <div style={{ height: 18, borderRadius: 'var(--radius-full)', overflow: 'hidden',
        display: 'flex', marginBottom: 12 }}>
        {segments.map(s => (
          s.pct > 0 && (
            <div key={s.label} style={{ width: `${s.pct}%`, background: s.color,
              transition: 'width 1s ease', position: 'relative' }}
              title={`${s.label}: ${s.pct}%`} />
          )
        ))}
      </div>
      <div style={{ display: 'flex', gap: 20, flexWrap: 'wrap' }}>
        {segments.map(s => (
          <div key={s.label} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <div style={{ width: 10, height: 10, borderRadius: '50%', background: s.color }} />
            <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{s.label}</span>
            <span style={{ fontSize: 13, fontWeight: 700, color: s.color }}>{s.pct}%</span>
          </div>
        ))}
      </div>
    </div>
  )
}

const PoliticalColors = { Positive: '#00d4aa', Neutral: '#6c63ff', Negative: '#ff4757' }

export default function AudiencePanel({ audience }) {
  if (!audience) return null

  const cohorts = (audience.interest_cohort_list || []).slice(0, 8)

  return (
    <div>
      <p className="section-title">Audience Intelligence</p>
      <div className="grid-2">

        {/* Gender Split */}
        <div className="card" style={{ padding: 24 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
            <h4 style={{ fontSize: 15, fontWeight: 700 }}>👥 Gender Split</h4>
            <ConfidenceBadge level={audience.gender_confidence} />
          </div>
          <GenderBar
            female={audience.gender_female_pct}
            male={audience.gender_male_pct}
            unknown={audience.gender_unknown_pct}
          />
          <p className="tooltip-text" style={{ marginTop: 16 }}>
            Estimated from bio keywords, profile signals, and language distribution in comments.
          </p>
        </div>

        {/* Political Inclination */}
        <div className="card" style={{ padding: 24 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
            <h4 style={{ fontSize: 15, fontWeight: 700 }}>🗳️ Political Lean</h4>
            <ConfidenceBadge level={audience.political_confidence} />
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginTop: 8 }}>
            {['Negative', 'Neutral', 'Positive'].map(p => {
              const isActive = audience.political_inclination === p
              const color = PoliticalColors[p]
              return (
                <div key={p} style={{ flex: 1, textAlign: 'center', padding: '16px 8px',
                  borderRadius: 'var(--radius-md)',
                  background: isActive ? `${color}18` : 'transparent',
                  border: isActive ? `2px solid ${color}50` : '2px solid transparent',
                  transition: 'all 0.3s' }}>
                  <div style={{ fontFamily: 'var(--font-display)', fontSize: 26, marginBottom: 4 }}>
                    {p === 'Positive' ? '😊' : p === 'Neutral' ? '😐' : '😤'}
                  </div>
                  <div style={{ fontSize: 12, fontWeight: 600, color: isActive ? color : 'var(--text-muted)' }}>{p}</div>
                </div>
              )
            })}
          </div>
          <p className="tooltip-text" style={{ marginTop: 12 }}>
            Derived from political comments in audience engagement.
          </p>
        </div>

        {/* Interest Cohorts */}
        <div className="card" style={{ padding: 24, gridColumn: 'span 2' }}>
          <h4 style={{ fontSize: 15, fontWeight: 700, marginBottom: 20 }}>🎯 Interest Cohorts</h4>
          {cohorts.length === 0 ? (
            <p style={{ color: 'var(--text-muted)', fontSize: 13 }}>No strong interest signals detected.</p>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={cohorts} layout="vertical" margin={{ left: 0, right: 30, top: 0, bottom: 0 }}>
                <XAxis type="number" tick={{ fill: '#8892aa', fontSize: 11 }} axisLine={false} tickLine={false}
                  tickFormatter={v => `${v}%`} domain={[0, 'dataMax + 5']} />
                <YAxis type="category" dataKey="cohort" tick={{ fill: '#4b5472', fontSize: 12 }}
                  axisLine={false} tickLine={false} width={160} />
                <Tooltip
                  formatter={(value, _, entry) => [`${value}% (${entry.payload.confidence} confidence)`, 'Audience share']}
                  contentStyle={{ background: 'white', border: '1px solid rgba(108,99,255,0.15)', borderRadius: 'var(--radius-md)', fontSize: 12, boxShadow: '0 4px 16px rgba(0,0,0,0.08)' }}
                  labelStyle={{ color: '#0f172a' }}
                />
                <Bar dataKey="percentage" radius={[0, 4, 4, 0]} maxBarSize={18}>
                  {cohorts.map((entry, i) => {
                    const colors = ['#6c63ff', '#00d4aa', '#ff6b9d', '#ffb347', '#3ecfff', '#ff4757', '#a78bfa', '#34d399']
                    return <Cell key={i} fill={colors[i % colors.length]} />
                  })}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </div>
  )
}
