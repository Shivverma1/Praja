import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts'
import { AlertTriangle } from 'lucide-react'

const DIMENSION_CONFIG = [
  {
    key: 'authenticity_breakdown',
    title: 'Authenticity',
    subtitle: 'Genuine vs Spam',
    colors: { Genuine: '#00d4aa', Spam: '#ff4757' },
    highlight: (data) => {
      const gen = data.Genuine || 0
      const total = Object.values(data).reduce((a, b) => a + b, 0)
      return total ? `${((gen/total)*100).toFixed(1)}% Genuine` : ''
    }
  },
  {
    key: 'bot_likelihood_breakdown',
    title: 'Bot Likelihood',
    subtitle: 'Human / Uncertain / Bot',
    colors: { Human: '#00d4aa', Uncertain: '#ffb347', 'Likely-bot': '#ff4757' },
  },
  {
    key: 'political_breakdown',
    title: 'Political Inclination',
    subtitle: 'Comment political lean',
    colors: { Positive: '#00d4aa', Neutral: '#6c63ff', Negative: '#ff4757', 'N/A': '#4a5168' },
  },
  {
    key: 'relevance_breakdown',
    title: 'Relevance',
    subtitle: 'On-topic vs Off-topic',
    colors: { 'On-topic': '#6c63ff', 'Off-topic': '#ff6b9d' },
  },
  {
    key: 'type_breakdown',
    title: 'Comment Type',
    subtitle: 'Praise / Question / etc.',
    colors: {
      Praise: '#00d4aa', Question: '#6c63ff', Criticism: '#ff4757',
      'Tag-a-friend': '#ffb347', 'Sales-or-promo': '#ff6b9d', Other: '#4a5168',
    },
  },
  {
    key: 'language_breakdown',
    title: 'Language / Script',
    subtitle: 'English / Hindi / Hinglish',
    colors: { English: '#6c63ff', Hindi: '#ff6b9d', Hinglish: '#ffb347', Regional: '#00d4aa', Ambiguous: '#4a5168' },
  },
]

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null
  const { name, value } = payload[0]
  return (
    <div style={{
      padding: '8px 14px', borderRadius: 'var(--radius-sm)', fontSize: 12,
      background: 'white', border: '1px solid rgba(108,99,255,0.15)',
      boxShadow: '0 4px 16px rgba(0,0,0,0.08)',
    }}>
      <span style={{ color: 'var(--text-secondary)' }}>{name}: </span>
      <strong style={{ color: 'var(--text-primary)' }}>{value}</strong>
    </div>
  )
}

function DimensionPie({ config, data }) {
  const entries = Object.entries(data || {}).filter(([, v]) => v > 0)
  const total = entries.reduce((a, [, v]) => a + v, 0)
  const chartData = entries.map(([name, value]) => ({ name, value }))
  const highlight = config.highlight?.(data || {})

  return (
    <div className="card" style={{ padding: 20, display: 'flex', flexDirection: 'column', gap: 12 }}>
      <div>
        <h4 style={{ fontSize: 14, fontWeight: 700, marginBottom: 2 }}>{config.title}</h4>
        <p style={{ fontSize: 12, color: 'var(--text-muted)' }}>{config.subtitle}</p>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <ResponsiveContainer width={90} height={90}>
          <PieChart>
            <Pie data={chartData} cx="50%" cy="50%" innerRadius={28} outerRadius={42}
              paddingAngle={2} dataKey="value" strokeWidth={0}>
              {chartData.map(({ name }) => (
                <Cell key={name} fill={config.colors[name] || '#6c63ff'} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
          </PieChart>
        </ResponsiveContainer>

        {/* Legend */}
        <div style={{ flex: 1 }}>
          {chartData.slice(0, 4).map(({ name, value }) => (
            <div key={name} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              marginBottom: 4, gap: 8 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <div style={{ width: 8, height: 8, borderRadius: '50%',
                  background: config.colors[name] || '#6c63ff', flexShrink: 0 }} />
                <span style={{ fontSize: 11, color: 'var(--text-secondary)' }}>{name}</span>
              </div>
              <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
                <span style={{ fontSize: 11, color: 'var(--text-primary)', fontWeight: 600 }}>{value}</span>
                <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>
                  {total ? `${((value/total)*100).toFixed(0)}%` : ''}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {highlight && (
        <div style={{ padding: '6px 12px', borderRadius: 'var(--radius-sm)',
          background: 'rgba(0,212,170,0.08)', border: '1px solid rgba(0,212,170,0.2)',
          fontSize: 12, color: 'var(--accent-secondary)', fontWeight: 600 }}>
          {highlight}
        </div>
      )}
    </div>
  )
}

export default function CommentClassificationPanel({ summary }) {
  if (!summary) return null

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16, flexWrap: 'wrap', gap: 8 }}>
        <p className="section-title" style={{ margin: 0 }}>Comment Classification</p>
        <div style={{ display: 'flex', gap: 12, fontSize: 13, color: 'var(--text-secondary)' }}>
          <span><strong style={{ color: 'var(--text-primary)' }}>{summary.total_comments}</strong> total comments</span>
          {summary.manual_review_count > 0 && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 4, color: 'var(--accent-amber)' }}>
              <AlertTriangle size={12} />
              {summary.manual_review_count} need manual review
            </div>
          )}
        </div>
      </div>

      <div className="grid-3" style={{ gridTemplateColumns: 'repeat(3, 1fr)' }}>
        {DIMENSION_CONFIG.map(config => (
          <DimensionPie key={config.key} config={config} data={summary[config.key]} />
        ))}
      </div>
    </div>
  )
}
