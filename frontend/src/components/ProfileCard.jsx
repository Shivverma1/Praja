import { CheckCircle, Link, Users, UserPlus, Grid } from 'lucide-react'

function fmt(n) {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(2) + 'M'
  if (n >= 1_000) return (n / 1_000).toFixed(1) + 'K'
  return n
}

export default function ProfileCard({ creator, metrics }) {
  const er      = metrics?.engagement_rate ?? 0
  const erColor = er >= 6 ? '#CC5200' : er >= 3 ? '#FF9933' : '#F5A030'
  const erLabel = er >= 6 ? 'EXCELLENT' : er >= 3 ? 'AVERAGE' : 'LOW'

  return (
    <div style={{
      background: 'var(--surface)',
      border: '1px solid var(--rule)',
      borderRadius: 'var(--r-xl)',
      padding: '32px 36px',
      boxShadow: 'var(--shadow-card)',
      display: 'flex', gap: 36, alignItems: 'flex-start', flexWrap: 'wrap',
    }}>

      {/* Avatar */}
      <div style={{ position: 'relative', flexShrink: 0 }}>
        <img
          src={creator.profile_pic_url || `https://api.dicebear.com/7.x/initials/svg?seed=${creator.handle}`}
          alt={creator.display_name}
          style={{
            width: 88, height: 88, borderRadius: 'var(--r-lg)',
            objectFit: 'cover',
            border: '2px solid var(--rule-strong)',
          }}
        />
        {creator.verified && (
          <div style={{
            position: 'absolute', bottom: -4, right: -4,
            width: 20, height: 20, borderRadius: '50%',
            background: 'var(--chart)', border: '2px solid var(--surface)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <CheckCircle size={10} color="white" strokeWidth={3} />
          </div>
        )}
      </div>

      {/* Info */}
      <div style={{ flex: 1, minWidth: 200 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap', marginBottom: 2 }}>
          <h2 style={{
            fontFamily: 'var(--font-display)',
            fontSize: 22, fontWeight: 800,
            letterSpacing: '-0.02em',
            color: 'var(--ink-1)',
          }}>
            {creator.display_name || `@${creator.handle}`}
          </h2>
          {creator.verified && (
            <span className="badge badge-blue">Verified</span>
          )}
        </div>

        <p style={{
          fontFamily: 'var(--font-data)', fontSize: 12,
          color: 'var(--ink-3)', marginBottom: 12,
          letterSpacing: '0.04em',
        }}>
          @{creator.handle}
        </p>

        {creator.bio && (
          <p style={{
            fontSize: 14, color: 'var(--ink-2)',
            lineHeight: 1.65, marginBottom: 12, maxWidth: 440,
          }}>
            {creator.bio}
          </p>
        )}

        {creator.external_link && (
          <a
            href={creator.external_link} target="_blank" rel="noopener noreferrer"
            style={{
              display: 'inline-flex', alignItems: 'center', gap: 6,
              fontFamily: 'var(--font-data)', fontSize: 11,
              color: 'var(--chart)', letterSpacing: '0.04em',
            }}
          >
            <Link size={11} />
            {creator.external_link.replace(/^https?:\/\//, '')}
          </a>
        )}
      </div>

      {/* Stats — DM Mono readouts */}
      <div style={{ display: 'flex', gap: 36, flexWrap: 'wrap', alignItems: 'flex-start' }}>
        {[
          { icon: Users,   label: 'FOLLOWERS', value: fmt(creator.follower_count)  },
          { icon: UserPlus, label: 'FOLLOWING', value: fmt(creator.following_count) },
          { icon: Grid,    label: 'POSTS',      value: fmt(creator.post_count)      },
        ].map(({ icon: Icon, label, value }) => (
          <div key={label}>
            <div style={{
              fontFamily: 'var(--font-data)', fontSize: 10,
              color: 'var(--ink-4)', letterSpacing: '0.12em',
              marginBottom: 4,
              display: 'flex', alignItems: 'center', gap: 4,
            }}>
              <Icon size={9} /> {label}
            </div>
            <div style={{
              fontFamily: 'var(--font-data)',
              fontSize: 22, fontWeight: 500,
              color: 'var(--ink-1)',
              letterSpacing: '-0.02em',
            }}>
              {value}
            </div>
          </div>
        ))}

        {/* ER indicator */}
        <div style={{
          paddingLeft: 28,
          borderLeft: '1px solid var(--rule)',
        }}>
          <div style={{
            fontFamily: 'var(--font-data)', fontSize: 10,
            color: 'var(--ink-4)', letterSpacing: '0.12em',
            marginBottom: 4,
          }}>
            ENG. RATE
          </div>
          <div style={{
            fontFamily: 'var(--font-data)',
            fontSize: 22, fontWeight: 500,
            color: erColor, letterSpacing: '-0.02em',
          }}>
            {er.toFixed(2)}%
          </div>
          <div style={{
            fontFamily: 'var(--font-data)', fontSize: 9,
            color: erColor, letterSpacing: '0.12em',
            marginTop: 2,
          }}>
            {erLabel}
          </div>
        </div>
      </div>
    </div>
  )
}
