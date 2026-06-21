import { useState } from 'react'
import { Heart, MessageCircle, Bookmark, Tag } from 'lucide-react'

function fmt(n) {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + 'M'
  if (n >= 1_000) return (n / 1_000).toFixed(1) + 'K'
  return n
}

function PostCard({ post, onClick }) {
  const [imgErr, setImgErr] = useState(false)

  return (
    <div
      id={`post-card-${post.id}`}
      className="card"
      style={{ cursor: 'pointer', overflow: 'hidden', transition: 'transform 0.2s', position: 'relative' }}
      onClick={() => onClick(post)}
      onMouseEnter={e => e.currentTarget.style.transform = 'translateY(-4px)'}
      onMouseLeave={e => e.currentTarget.style.transform = 'translateY(0)'}
    >
      {/* Thumbnail */}
      <div style={{ aspectRatio: '1/1', background: 'var(--bg-surface)', position: 'relative', overflow: 'hidden' }}>
        {!imgErr && post.thumbnail_url ? (
          <img src={post.thumbnail_url} alt="post" onError={() => setImgErr(true)}
            style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
        ) : (
          <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center',
            background: `linear-gradient(135deg, #eef0fb 0%, #e6eaf8 100%)`, fontSize: 32 }}>
            📸
          </div>
        )}
        {/* Collab badge */}
        {post.is_collaboration && (
          <div style={{ position: 'absolute', top: 8, left: 8 }}>
            <span className="badge badge-amber" style={{ fontSize: 9 }}>
              <Tag size={9} /> Collab
            </span>
          </div>
        )}
      </div>

      {/* Stats row */}
      <div style={{ padding: '10px 12px', display: 'flex', gap: 12, justifyContent: 'space-around' }}>
        {[
          { icon: Heart, value: fmt(post.likes), color: '#ff6b9d' },
          { icon: MessageCircle, value: fmt(post.comments_count), color: '#6c63ff' },
          { icon: Bookmark, value: fmt(post.saves), color: '#00d4aa' },
        ].map(({ icon: Icon, value, color }) => (
          <div key={color} style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 12 }}>
            <Icon size={11} color={color} />
            <span style={{ color: 'var(--text-secondary)', fontWeight: 500 }}>{value}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function PostModal({ post, onClose }) {
  if (!post) return null
  return (
    <div onClick={onClose} style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.75)',
      backdropFilter: 'blur(8px)', display: 'flex', alignItems: 'center', justifyContent: 'center',
      zIndex: 200, padding: 20 }}>
      <div onClick={e => e.stopPropagation()} className="card"
        style={{ maxWidth: 540, width: '100%', padding: 28, maxHeight: '80vh', overflow: 'auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 }}>
          <div>
            <h3 style={{ fontSize: 16, marginBottom: 4 }}>
              {post.is_collaboration ? '🤝 Collaboration Post' : '📸 Personal Post'}
            </h3>
            <p style={{ fontSize: 12, color: 'var(--text-muted)' }}>
              {post.posted_at ? new Date(post.posted_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' }) : ''}
            </p>
          </div>
          <button onClick={onClose} style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: 20 }}>✕</button>
        </div>

        {post.caption && (
          <p style={{ fontSize: 14, color: 'var(--text-secondary)', lineHeight: 1.7, marginBottom: 16,
            maxHeight: 120, overflow: 'auto' }}>
            {post.caption}
          </p>
        )}

        {/* Stats */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 16 }}>
          {[
            { label: 'Likes', value: post.likes?.toLocaleString(), color: '#ff6b9d' },
            { label: 'Comments', value: post.comments_count?.toLocaleString(), color: '#6c63ff' },
            { label: 'Saves', value: post.saves?.toLocaleString(), color: '#00d4aa' },
            { label: 'Shares', value: post.shares?.toLocaleString(), color: '#3ecfff' },
          ].map(({ label, value, color }) => (
            <div key={label} style={{ textAlign: 'center', padding: '12px 8px',
              background: `${color}10`, borderRadius: 'var(--radius-sm)', border: `1px solid ${color}20` }}>
              <div style={{ fontFamily: 'var(--font-display)', fontSize: 18, fontWeight: 700, color }}>{value || '—'}</div>
              <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 2 }}>{label}</div>
            </div>
          ))}
        </div>

        {/* Hashtags */}
        {post.hashtag_list?.length > 0 && (
          <div className="chip-bar">
            {post.hashtag_list.map(tag => (
              <span key={tag} className="chip" style={{ fontSize: 11, color: 'var(--accent-primary-light)' }}>{tag}</span>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default function PostGrid({ posts }) {
  const [selectedPost, setSelectedPost] = useState(null)

  if (!posts?.length) return null

  return (
    <div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))', gap: 12 }}>
        {posts.map(post => (
          <PostCard key={post.id} post={post} onClick={setSelectedPost} />
        ))}
      </div>
      <PostModal post={selectedPost} onClose={() => setSelectedPost(null)} />
    </div>
  )
}
