export default function HashtagCloud({ hashtags, hideTitle = false }) {
  if (!hashtags?.length) return null

  const maxCount = Math.max(...hashtags.map(h => h.count))

  return (
    <div>
      {!hideTitle && <p className="section-title">Top Hashtags</p>}
      <div className="card" style={{ padding: 24 }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10, alignItems: 'center' }}>
          {hashtags.map(({ tag, count }, i) => {
            const ratio = count / maxCount
            const size = 11 + Math.round(ratio * 10)   // 11–21px
            const opacity = 0.5 + ratio * 0.5
            const colors = ['#6c63ff', '#00d4aa', '#ff6b9d', '#ffb347', '#3ecfff', '#a78bfa']
            const color = colors[i % colors.length]
            return (
              <span key={tag} style={{
                fontSize: size,
                fontWeight: ratio > 0.6 ? 700 : ratio > 0.3 ? 600 : 500,
                color,
                opacity,
                padding: `${4 + ratio * 4}px ${8 + ratio * 6}px`,
                background: `${color}12`,
                border: `1px solid ${color}25`,
                borderRadius: 'var(--radius-full)',
                cursor: 'default',
                transition: 'all 0.2s',
                lineHeight: 1,
              }}
                title={`${count} posts`}
                onMouseEnter={e => { e.currentTarget.style.opacity = '1'; e.currentTarget.style.transform = 'scale(1.08)' }}
                onMouseLeave={e => { e.currentTarget.style.opacity = String(opacity); e.currentTarget.style.transform = 'scale(1)' }}
              >
                {tag}
              </span>
            )
          })}
        </div>
      </div>
    </div>
  )
}
