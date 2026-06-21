const STEPS = [
  { threshold: 5,   label: 'Fetching Instagram profile' },
  { threshold: 20,  label: 'Loading 12 recent posts'    },
  { threshold: 55,  label: 'AI comment classification'  },
  { threshold: 75,  label: 'Computing engagement metrics' },
  { threshold: 88,  label: 'Estimating audience demographics' },
  { threshold: 100, label: 'Analysis complete'          },
]

export default function PipelineProgress({ status, progress, message }) {
  const isError    = status === 'error'
  const isComplete = status === 'complete'
  const isRunning  = !isError && !isComplete

  return (
    <div style={{ maxWidth: 480, margin: '80px auto', padding: '0 20px' }}>

      {/* Terminal card */}
      <div style={{
        background: 'var(--ink-1)',
        borderRadius: 'var(--r-xl)',
        overflow: 'hidden',
        boxShadow: '0 24px 64px rgba(12,19,34,0.2)',
      }}>

        {/* Title bar */}
        <div style={{
          background: 'rgba(255,255,255,0.06)',
          borderBottom: '1px solid rgba(255,255,255,0.08)',
          padding: '12px 20px',
          display: 'flex', alignItems: 'center', gap: 8,
        }}>
          <div style={{ width: 10, height: 10, borderRadius: '50%', background: 'var(--signal)' }} />
          <div style={{ width: 10, height: 10, borderRadius: '50%', background: 'var(--amber)' }} />
          <div style={{ width: 10, height: 10, borderRadius: '50%', background: 'var(--go)' }} />
          <span style={{
            fontFamily: 'var(--font-data)', fontSize: 11,
            color: 'rgba(255,255,255,0.3)', marginLeft: 12,
            letterSpacing: '0.06em',
          }}>
            praja — analysis pipeline
          </span>
        </div>

        {/* Terminal body */}
        <div style={{ padding: '28px 24px' }}>

          {/* Steps as terminal output */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginBottom: 28 }}>
            {STEPS.map(({ threshold, label }) => {
              const done   = progress >= threshold
              const active = progress >= threshold - 18 && progress < threshold && isRunning

              return (
                <div key={label} style={{
                  display: 'flex', alignItems: 'center', gap: 12,
                  fontFamily: 'var(--font-data)', fontSize: 12,
                  opacity: done ? 1 : active ? 0.85 : 0.28,
                  transition: 'opacity 0.4s',
                }}>
                  {/* Prefix */}
                  <span style={{
                    color: done ? 'var(--go)' : active ? 'var(--amber)' : 'rgba(255,255,255,0.4)',
                    fontSize: 11, width: 14, flexShrink: 0, textAlign: 'center',
                  }}>
                    {done ? '✓' : active ? '›' : '·'}
                  </span>

                  <span style={{ color: done ? '#fff' : active ? 'rgba(255,255,255,0.9)' : 'rgba(255,255,255,0.4)' }}>
                    {label}
                  </span>

                  {/* Blinking cursor on active step */}
                  {active && (
                    <span style={{
                      display: 'inline-block', width: 7, height: 13,
                      background: 'var(--amber)',
                      borderRadius: 1,
                      animation: 'blink 1s step-end infinite',
                      flexShrink: 0,
                    }} />
                  )}
                </div>
              )
            })}
          </div>

          {/* Progress line */}
          {!isError && (
            <div>
              <div style={{
                height: 2, background: 'rgba(255,255,255,0.08)',
                borderRadius: 'var(--r-full)', overflow: 'hidden',
                marginBottom: 8,
              }}>
                <div style={{
                  height: '100%',
                  width: `${progress}%`,
                  background: isComplete ? 'var(--go)' : 'var(--signal)',
                  borderRadius: 'var(--r-full)',
                  transition: 'width 0.6s ease',
                }} />
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontFamily: 'var(--font-data)', fontSize: 10, color: 'rgba(255,255,255,0.25)', letterSpacing: '0.06em' }}>
                  {message || 'Initializing…'}
                </span>
                <span style={{
                  fontFamily: 'var(--font-data)', fontSize: 11, fontWeight: 500,
                  color: isComplete ? 'var(--go)' : 'var(--signal)',
                }}>
                  {progress}%
                </span>
              </div>
            </div>
          )}

          {/* Error state */}
          {isError && (
            <div style={{
              fontFamily: 'var(--font-data)', fontSize: 12,
              color: 'var(--signal)',
              padding: '12px 16px',
              background: 'rgba(232,41,74,0.1)',
              border: '1px solid rgba(232,41,74,0.2)',
              borderRadius: 'var(--r-md)',
            }}>
              ✗ {message || 'Pipeline failed. Try again.'}
            </div>
          )}
        </div>
      </div>

      {/* Status text below card */}
      <p style={{
        textAlign: 'center', marginTop: 20,
        fontFamily: 'var(--font-data)', fontSize: 11,
        color: 'var(--ink-3)', letterSpacing: '0.08em',
      }}>
        {isComplete ? 'LOADING DASHBOARD…' : isError ? 'ANALYSIS FAILED' : 'PIPELINE RUNNING…'}
      </p>
    </div>
  )
}
