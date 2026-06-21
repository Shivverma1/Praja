import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowRight, Loader } from 'lucide-react'
import { analyzeCreator } from '../services/api.js'

const DEMO_HANDLES = ['virat.kohli', 'priyankachopra', 'bhuvan.bam22', 'carry.minati', 'khabylame']

const FEATURES = [
  { n: '01', title: 'Comment Authenticity', desc: 'Every comment scored for bot likelihood, relevance, and genuine intent — not just a count.' },
  { n: '02', title: 'Real Engagement Rate', desc: 'Calculated from actual post data: likes, comments, saves, and shares per post divided by followers.' },
  { n: '03', title: 'Audience Segments', desc: 'Who actually engages — interest cohorts from beauty to finance, derived from content signals.' },
  { n: '04', title: 'Collaboration Score', desc: 'A single number that tells you if this creator is worth working with, based on all the data.' },
]

export default function LandingPage() {
  const navigate = useNavigate()
  const [handle, setHandle] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const submit = async (h) => {
    const cleaned = h.trim().replace(/^@/, '')
    if (!cleaned) return
    setLoading(true)
    setError('')
    try {
      await analyzeCreator(cleaned)
      navigate(`/creator/${cleaned}`)
    } catch {
      setError('Cannot reach backend. Is the server running on port 8000?')
      setLoading(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', background: '#fff', fontFamily: 'var(--font-body)' }}>

      {/* top bar */}
      <div style={{ height: 4, background: '#FF9933' }} />

      {/* Navbar */}
      <nav style={{
        position: 'sticky', top: 0, zIndex: 100,
        background: 'rgba(255,255,255,0.97)',
        backdropFilter: 'blur(20px)',
        borderBottom: '1px solid rgba(255,153,51,0.1)',
        padding: '14px 0',
      }}>
        <div className="container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{
              width: 34, height: 34, borderRadius: '50%', background: '#FF9933',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <circle cx="8" cy="8" r="2.5" fill="white"/>
                <line x1="8" y1="0.5" x2="8" y2="5" stroke="white" strokeWidth="1.5"/>
                <line x1="8" y1="11" x2="8" y2="15.5" stroke="white" strokeWidth="1.5"/>
                <line x1="0.5" y1="8" x2="5" y2="8" stroke="white" strokeWidth="1.5"/>
                <line x1="11" y1="8" x2="15.5" y2="8" stroke="white" strokeWidth="1.5"/>
              </svg>
            </div>
            <span style={{ fontFamily: 'var(--font-display)', fontSize: 22, fontWeight: 700, color: '#1A0E04', letterSpacing: '0.06em' }}>
              PRAJA
            </span>
          </div>
          <span style={{ fontFamily: 'var(--font-data)', fontSize: 10, color: 'rgba(26,14,4,0.45)', letterSpacing: '0.14em' }}>
            CREATOR INTELLIGENCE
          </span>
        </div>
      </nav>

      {/* Hero */}
      <div className="container" style={{ paddingTop: 80, paddingBottom: 80 }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0,1.1fr) minmax(0,0.9fr)', gap: 64, alignItems: 'center' }}>

          {/* Headline */}
          <div>
            <div style={{
              display: 'inline-flex', alignItems: 'center', gap: 8,
              border: '1px solid rgba(255,153,51,0.3)', borderRadius: 4,
              padding: '5px 12px', marginBottom: 28, background: 'rgba(255,153,51,0.06)',
            }}>
              <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#FF9933' }} />
              <span style={{ fontFamily: 'var(--font-data)', fontSize: 10, color: '#1A0E04', letterSpacing: '0.14em' }}>
                INSTAGRAM ANALYTICS PLATFORM
              </span>
            </div>

            <h1 style={{
              fontFamily: 'var(--font-display)',
              fontSize: 'clamp(44px, 5.5vw, 76px)',
              fontWeight: 700, lineHeight: 1.04, letterSpacing: '0.01em',
              color: '#1A0E04', marginBottom: 24,
            }}>
              Know what your<br />audience<br />
              <span style={{ color: '#FF9933' }}>really thinks.</span>
            </h1>

            <p style={{ fontSize: 16, lineHeight: 1.8, color: 'rgba(26,14,4,0.5)', maxWidth: 420, marginBottom: 32 }}>
              Enter any Instagram handle and get engagement quality, comment authenticity,
              audience demographics, and a collaboration score — in about 30 seconds.
              No API keys, no sign-up.
            </p>

            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
              {['No API keys', 'Works on any handle', 'Results in 30s', 'Demo mode included'].map(f => (
                <span key={f} style={{
                  fontFamily: 'var(--font-data)', fontSize: 10, padding: '5px 11px',
                  letterSpacing: '0.06em', border: '1px solid rgba(255,153,51,0.2)',
                  borderRadius: 4, color: 'rgba(26,14,4,0.45)', background: 'rgba(255,153,51,0.03)',
                }}>
                  {f}
                </span>
              ))}
            </div>
          </div>

          {/* Search card */}
          <div>
            <div style={{ height: 4, borderRadius: '8px 8px 0 0', background: '#FF9933' }} />
            <div style={{
              background: '#fff', border: '1px solid rgba(255,153,51,0.18)',
              borderTop: 'none', borderRadius: '0 0 12px 12px',
              padding: 28, boxShadow: '0 8px 40px rgba(255,153,51,0.10)',
            }}>
              <div style={{ fontFamily: 'var(--font-display)', fontSize: 14, fontWeight: 600, letterSpacing: '0.1em', color: '#FF9933', marginBottom: 16 }}>
                ANALYZE A CREATOR
              </div>

              <div style={{
                display: 'flex', alignItems: 'center',
                border: '1.5px solid rgba(255,153,51,0.25)', borderRadius: 8,
                background: '#fff', marginBottom: 12,
              }}>
                <span style={{ fontFamily: 'var(--font-data)', fontSize: 17, color: '#FF9933', padding: '12px 4px 12px 14px', lineHeight: 1 }}>@</span>
                <input
                  style={{
                    flex: 1, border: 'none', background: 'transparent',
                    fontFamily: 'var(--font-body)', fontSize: 14,
                    color: '#1A0E04', padding: '12px 14px 12px 4px', outline: 'none',
                  }}
                  placeholder="instagram_handle"
                  value={handle}
                  onChange={e => setHandle(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && submit(handle)}
                  disabled={loading}
                  autoFocus
                />
              </div>

              <button
                style={{
                  width: '100%', display: 'flex', alignItems: 'center',
                  justifyContent: 'center', gap: 8,
                  background: handle.trim() && !loading ? '#FF9933' : 'rgba(255,153,51,0.25)',
                  color: '#fff', border: 'none',
                  cursor: handle.trim() && !loading ? 'pointer' : 'default',
                  fontFamily: 'var(--font-display)', fontSize: 14, fontWeight: 600,
                  letterSpacing: '0.08em', padding: '13px 20px', borderRadius: 8,
                  transition: 'background 0.2s',
                  boxShadow: handle.trim() && !loading ? '0 4px 18px rgba(255,153,51,0.3)' : 'none',
                }}
                onClick={() => submit(handle)}
                disabled={loading || !handle.trim()}
              >
                {loading
                  ? <><Loader size={14} style={{ animation: 'spin 0.75s linear infinite' }} /> Analyzing…</>
                  : <>Run Analysis <ArrowRight size={14} /></>
                }
              </button>

              {error && (
                <p style={{
                  fontFamily: 'var(--font-data)', fontSize: 11, color: '#FF9933',
                  marginTop: 10, padding: '8px 12px', background: 'rgba(255,153,51,0.06)',
                  borderRadius: 6, border: '1px solid rgba(255,153,51,0.2)',
                }}>
                  {error}
                </p>
              )}

              <div style={{ display: 'flex', alignItems: 'center', gap: 10, margin: '18px 0' }}>
                <div style={{ flex: 1, height: 1, background: 'rgba(255,153,51,0.12)' }} />
                <span style={{ fontFamily: 'var(--font-data)', fontSize: 9, color: 'rgba(26,14,4,0.3)', letterSpacing: '0.14em' }}>
                  OR TRY A DEMO
                </span>
                <div style={{ flex: 1, height: 1, background: 'rgba(255,153,51,0.12)' }} />
              </div>

              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                {DEMO_HANDLES.map(h => (
                  <button
                    key={h}
                    onClick={() => submit(h)}
                    disabled={loading}
                    style={{
                      fontFamily: 'var(--font-data)', fontSize: 10, padding: '5px 10px',
                      letterSpacing: '0.05em', border: '1px solid rgba(255,153,51,0.2)',
                      borderRadius: 4, background: '#fff', color: 'rgba(26,14,4,0.5)',
                      cursor: 'pointer', transition: 'all 0.15s',
                    }}
                    onMouseEnter={e => { e.currentTarget.style.borderColor = '#FF9933'; e.currentTarget.style.color = '#FF9933' }}
                    onMouseLeave={e => { e.currentTarget.style.borderColor = 'rgba(255,153,51,0.2)'; e.currentTarget.style.color = 'rgba(26,14,4,0.5)' }}
                  >
                    @{h}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Stats strip — orange bg */}
      <div style={{ background: '#FF9933', padding: '22px 0' }}>
        <div className="container">
          <div style={{ display: 'flex', gap: 48, flexWrap: 'wrap', justifyContent: 'center' }}>
            {[['12','posts per analysis'],['6','comment dimensions'],['10+','audience segments'],['~30s','to results']].map(([v, l]) => (
              <div key={v} style={{ display: 'flex', alignItems: 'baseline', gap: 10 }}>
                <span style={{ fontFamily: 'var(--font-data)', fontSize: 26, fontWeight: 500, color: '#fff', letterSpacing: '-0.02em' }}>{v}</span>
                <span style={{ fontFamily: 'var(--font-data)', fontSize: 10, color: 'rgba(255,255,255,0.65)', letterSpacing: '0.08em' }}>{l}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Video embed — white section */}
      <div style={{ background: '#fff', padding: '72px 0', borderBottom: '1px solid rgba(255,153,51,0.1)' }}>
        <div className="container">
          <div style={{ textAlign: 'center', marginBottom: 40 }}>
            <div style={{ fontFamily: 'var(--font-data)', fontSize: 10, letterSpacing: '0.18em', color: 'rgba(26,14,4,0.45)', marginBottom: 12 }}>
              SEE IT IN ACTION
            </div>
            <h2 style={{ fontFamily: 'var(--font-display)', fontSize: 'clamp(26px,3vw,42px)', fontWeight: 700, color: '#1A0E04', letterSpacing: '0.02em' }}>
              Watch How Praja Works
            </h2>
          </div>

          <div style={{
            position: 'relative', paddingBottom: '56.25%', height: 0,
            borderRadius: 12, overflow: 'hidden',
            border: '1px solid rgba(255,153,51,0.15)',
            boxShadow: '0 20px 60px rgba(255,153,51,0.12), 0 4px 16px rgba(26,14,4,0.06)',
          }}>
            <iframe
              src="/launch-video.html"
              title="How Praja works"
              style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', border: 'none' }}
              allow="autoplay"
            />
          </div>

          <p style={{ textAlign: 'center', marginTop: 14, fontFamily: 'var(--font-data)', fontSize: 10, color: 'rgba(26,14,4,0.22)', letterSpacing: '0.1em' }}>
            Click the dots at the bottom to jump between scenes
          </p>
        </div>
      </div>

      {/* Features — very pale orange tint */}
      <div style={{ background: '#FFF8F2', padding: '72px 0' }}>
        <div className="container">
          <div style={{ fontFamily: 'var(--font-data)', fontSize: 10, letterSpacing: '0.16em', color: 'rgba(26,14,4,0.45)', textAlign: 'center', marginBottom: 48 }}>
            WHAT YOU GET IN THE REPORT
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 1, borderRadius: 12, overflow: 'hidden', border: '1px solid rgba(255,153,51,0.12)' }}>
            {FEATURES.map(({ n, title, desc }, i) => (
              <div
                key={n}
                style={{
                  background: '#fff', padding: '36px 32px',
                  borderRight: i % 2 === 0 ? '1px solid rgba(255,153,51,0.1)' : 'none',
                  borderBottom: i < 2 ? '1px solid rgba(255,153,51,0.1)' : 'none',
                  transition: 'background 0.15s',
                }}
                onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,153,51,0.025)'}
                onMouseLeave={e => e.currentTarget.style.background = '#fff'}
              >
                <div style={{ fontFamily: 'var(--font-data)', fontSize: 10, color: 'rgba(26,14,4,0.4)', letterSpacing: '0.12em', marginBottom: 14 }}>{n}</div>
                <h3 style={{ fontFamily: 'var(--font-display)', fontSize: 20, fontWeight: 700, color: '#1A0E04', marginBottom: 10, letterSpacing: '0.02em' }}>
                  {title}
                </h3>
                <p style={{ fontSize: 14, color: 'rgba(26,14,4,0.48)', lineHeight: 1.75 }}>{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* CTA — orange bg */}
      <div style={{ background: '#FF9933', padding: '60px 0', textAlign: 'center' }}>
        <div className="container">
          <div style={{ fontFamily: 'var(--font-data)', fontSize: 10, color: 'rgba(255,255,255,0.55)', letterSpacing: '0.16em', marginBottom: 16 }}>
            NO SIGN-UP · NO API KEYS · FREE TO TRY
          </div>
          <h2 style={{ fontFamily: 'var(--font-display)', fontSize: 'clamp(28px,4vw,52px)', fontWeight: 700, color: '#fff', marginBottom: 32, letterSpacing: '0.02em', lineHeight: 1.1 }}>
            Type a handle.<br />Get the truth.
          </h2>
          <button
            onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
            style={{
              display: 'inline-flex', alignItems: 'center', gap: 10,
              background: '#fff', color: '#FF9933', border: 'none', cursor: 'pointer',
              fontFamily: 'var(--font-display)', fontSize: 15, fontWeight: 700,
              letterSpacing: '0.06em', padding: '14px 32px', borderRadius: 8,
              boxShadow: '0 4px 20px rgba(0,0,0,0.14)', transition: 'transform 0.15s',
            }}
            onMouseEnter={e => e.currentTarget.style.transform = 'translateY(-1px)'}
            onMouseLeave={e => e.currentTarget.style.transform = 'none'}
          >
            Analyze a creator <ArrowRight size={15} />
          </button>
        </div>
      </div>

      {/* Footer */}
      <div style={{ height: 4, background: '#FF9933' }} />
      <div style={{ background: '#1A0E04', padding: '18px 0', textAlign: 'center' }}>
        <span style={{ fontFamily: 'var(--font-data)', fontSize: 10, color: 'rgba(255,255,255,0.18)', letterSpacing: '0.12em' }}>
          PRAJA · CREATOR INTELLIGENCE PLATFORM · 2026
        </span>
      </div>
    </div>
  )
}
