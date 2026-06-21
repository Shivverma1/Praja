import { Heart, MessageCircle, Share2, Bookmark, TrendingUp, Award } from 'lucide-react'

function fmt(n) {
  if (!n && n !== 0) return '—'
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(2) + 'M'
  if (n >= 1_000) return (n / 1_000).toFixed(1) + 'K'
  return String(n)
}

const SIGNAL_COLOR = '#FF9933'
const GO_COLOR    = '#CC5200'
const AMBER_COLOR = '#F5A030'

export default function MetricsSummary({ metrics, classificationSummary }) {
  if (!metrics) return null

  const gr = classificationSummary?.genuine_ratio ?? null
  const grColor  = gr > 0.7 ? GO_COLOR : gr > 0.4 ? AMBER_COLOR : SIGNAL_COLOR
  const grLabel  = gr !== null ? (gr > 0.7 ? 'Healthy' : gr > 0.4 ? 'Moderate' : 'High spam') : ''

  const CARDS = [
    {
      icon: Heart,
      label: 'AVG LIKES',
      value: fmt(Math.round(metrics.avg_likes)),
      color: SIGNAL_COLOR,
      sub: 'per post',
    },
    {
      icon: MessageCircle,
      label: 'AVG COMMENTS',
      value: fmt(Math.round(metrics.avg_comments)),
      color: '#CC5200',
      sub: 'per post',
    },
    {
      icon: Bookmark,
      label: 'AVG SAVES',
      value: fmt(Math.round(metrics.avg_saves)),
      color: GO_COLOR,
      sub: 'per post',
    },
    {
      icon: Share2,
      label: 'AVG SHARES',
      value: fmt(Math.round(metrics.avg_shares)),
      color: '#F5A030',
      sub: 'per post',
    },
    {
      icon: TrendingUp,
      label: 'ENGAGEMENT RATE',
      value: `${metrics.engagement_rate?.toFixed(2)}%`,
      color: AMBER_COLOR,
      sub: '(likes+comments+saves) / followers',
      featured: true,
    },
    {
      icon: Award,
      label: 'GENUINE COMMENTS',
      value: gr !== null ? `${(gr * 100).toFixed(1)}%` : '—',
      color: grColor,
      sub: grLabel,
    },
  ]

  return (
    <div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
        {CARDS.map(({ icon: Icon, label, value, color, sub, featured }) => (
          <div
            key={label}
            style={{
              background: 'var(--surface)',
              border: `1px solid ${featured ? color + '30' : 'var(--rule)'}`,
              borderTop: `3px solid ${featured ? color : 'var(--rule)'}`,
              borderRadius: 'var(--r-lg)',
              padding: '22px 20px 18px',
              boxShadow: featured
                ? `var(--shadow-card), 0 0 0 0 ${color}20`
                : 'var(--shadow-card)',
              transition: 'transform 0.15s, box-shadow 0.15s',
            }}
            onMouseEnter={e => {
              e.currentTarget.style.transform = 'translateY(-2px)'
              e.currentTarget.style.boxShadow = `var(--shadow-hover)`
            }}
            onMouseLeave={e => {
              e.currentTarget.style.transform = ''
              e.currentTarget.style.boxShadow = featured ? `var(--shadow-card)` : 'var(--shadow-card)'
            }}
          >
            {/* Label row */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
              <span style={{
                fontFamily: 'var(--font-data)',
                fontSize: 10, letterSpacing: '0.12em',
                color: 'var(--ink-3)',
              }}>
                {label}
              </span>
              <div style={{
                width: 28, height: 28, borderRadius: 'var(--r-sm)',
                background: `${color}12`, border: `1px solid ${color}20`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <Icon size={13} color={color} />
              </div>
            </div>

            {/* Value — DM Mono */}
            <div style={{
              fontFamily: 'var(--font-data)',
              fontSize: 32, fontWeight: 500,
              color, lineHeight: 1, marginBottom: 6,
              letterSpacing: '-0.02em',
            }}>
              {value}
            </div>

            {sub && (
              <div style={{
                fontFamily: 'var(--font-data)',
                fontSize: 10, color: 'var(--ink-4)',
                letterSpacing: '0.04em', lineHeight: 1.5,
              }}>
                {sub}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
