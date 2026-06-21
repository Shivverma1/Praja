import { useEffect, useState, useCallback, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, RotateCcw } from 'lucide-react'
import {
  getPipelineStatus, getCreator, getClassificationSummary,
  getPosts, getAudience, analyzeCreator
} from '../services/api.js'
import ProfileCard from '../components/ProfileCard.jsx'
import MetricsSummary from '../components/MetricsSummary.jsx'
import EngagementChart from '../components/EngagementChart.jsx'
import CommentClassificationPanel from '../components/CommentClassificationPanel.jsx'
import AudiencePanel from '../components/AudiencePanel.jsx'
import PostGrid from '../components/PostGrid.jsx'
import HashtagCloud from '../components/HashtagCloud.jsx'
import PipelineProgress from '../components/PipelineProgress.jsx'

const POLL_INTERVAL = 2000

function SectionLabel({ children }) {
  return (
    <div style={{
      fontFamily: 'var(--font-data)',
      fontSize: 10, fontWeight: 500,
      letterSpacing: '0.14em',
      textTransform: 'uppercase',
      color: 'var(--ink-3)',
      marginBottom: 20,
      display: 'flex', alignItems: 'center', gap: 12,
    }}>
      <span style={{ color: 'var(--signal)' }}>//</span>
      {children}
    </div>
  )
}

function Rule({ label }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 16, margin: '8px 0' }}>
      <div style={{ flex: 1, height: 1, background: 'var(--rule)' }} />
      <span style={{
        fontFamily: 'var(--font-data)', fontSize: 9,
        color: 'var(--ink-4)', letterSpacing: '0.16em', whiteSpace: 'nowrap',
      }}>
        {label}
      </span>
      <div style={{ flex: 1, height: 1, background: 'var(--rule)' }} />
    </div>
  )
}

export default function DashboardPage() {
  const { handle } = useParams()
  const navigate = useNavigate()
  const pollRef = useRef(null)

  const [pipelineStatus, setPipelineStatus] = useState({ status: 'pending', progress: 0, message: '' })
  const [creator, setCreator] = useState(null)
  const [posts, setPosts] = useState([])
  const [classificationSummary, setClassificationSummary] = useState(null)
  const [audience, setAudience] = useState(null)
  const [error, setError] = useState(null)
  const [refreshing, setRefreshing] = useState(false)

  const loadDashboard = useCallback(async () => {
    try {
      const [creatorRes, postsRes, classRes, audRes] = await Promise.allSettled([
        getCreator(handle),
        getPosts(handle),
        getClassificationSummary(handle),
        getAudience(handle),
      ])
      if (creatorRes.status === 'fulfilled') setCreator(creatorRes.value.data)
      if (postsRes.status === 'fulfilled') setPosts(postsRes.value.data)
      if (classRes.status === 'fulfilled') setClassificationSummary(classRes.value.data)
      if (audRes.status === 'fulfilled') setAudience(audRes.value.data)
    } catch (err) {
      console.error('Dashboard load error:', err)
    }
  }, [handle])

  const pollStatus = useCallback(async () => {
    try {
      const res = await getPipelineStatus(handle)
      const statusData = res.data
      setPipelineStatus(statusData)
      if (statusData.status === 'complete') {
        clearInterval(pollRef.current)
        await loadDashboard()
      } else if (statusData.status === 'error') {
        clearInterval(pollRef.current)
        setError(statusData.message || 'Pipeline failed.')
      }
    } catch (err) {
      if (err.response?.status === 404) {
        try { await analyzeCreator(handle) } catch { /* ok */ }
      }
    }
  }, [handle, loadDashboard])

  useEffect(() => {
    pollStatus()
    pollRef.current = setInterval(pollStatus, POLL_INTERVAL)
    return () => clearInterval(pollRef.current)
  }, [pollStatus])

  const handleRefresh = async () => {
    setRefreshing(true)
    setCreator(null); setPosts([]); setClassificationSummary(null)
    setAudience(null); setError(null)
    setPipelineStatus({ status: 'pending', progress: 0, message: '' })
    await analyzeCreator(handle, true)
    pollRef.current = setInterval(pollStatus, POLL_INTERVAL)
    setRefreshing(false)
  }

  const isLoading = pipelineStatus.status !== 'complete' && pipelineStatus.status !== 'error'

  return (
    <div style={{ minHeight: '100vh', background: 'var(--canvas)', position: 'relative' }}>

      {/* Navbar */}
      <nav style={{
        position: 'sticky', top: 0, zIndex: 100,
        padding: '13px 0',
        background: 'rgba(255,255,255,0.97)',
        backdropFilter: 'blur(20px)',
        borderBottom: '1px solid var(--rule)',
      }}>
        <div className="container navbar-inner">
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <button className="btn btn-ghost" style={{ padding: '7px 12px', fontSize: 13, gap: 6 }}
              onClick={() => navigate('/')}>
              <ArrowLeft size={14} /> Back
            </button>
            <span style={{
              fontFamily: 'var(--font-display)', fontSize: 18, fontWeight: 800,
              color: 'var(--signal)', letterSpacing: '-0.02em',
            }}>
              Praja
            </span>
            <span style={{
              fontFamily: 'var(--font-data)', fontSize: 11,
              color: 'var(--ink-3)', letterSpacing: '0.04em',
            }}>
              / @{handle}
            </span>
          </div>

          <button
            className="btn btn-ghost"
            style={{ padding: '7px 12px', fontSize: 12, gap: 6 }}
            onClick={handleRefresh}
            disabled={isLoading || refreshing}
          >
            <RotateCcw size={12} style={{ animation: isLoading ? 'spin 1s linear infinite' : 'none' }} />
            {isLoading ? 'Analyzing…' : 'Re-analyze'}
          </button>
        </div>
      </nav>

      <div className="container" style={{ paddingTop: 36, paddingBottom: 64, position: 'relative', zIndex: 1 }}>

        {/* Loading */}
        {isLoading && (
          <PipelineProgress
            status={pipelineStatus.status}
            progress={pipelineStatus.progress}
            message={pipelineStatus.message}
          />
        )}

        {/* Error */}
        {error && !isLoading && (
          <div style={{ maxWidth: 440, margin: '80px auto', textAlign: 'center' }}>
            <div style={{
              fontFamily: 'var(--font-data)', fontSize: 11,
              color: 'var(--signal)', letterSpacing: '0.1em', marginBottom: 16,
            }}>
              // PIPELINE ERROR
            </div>
            <div style={{
              background: 'var(--surface)', border: '1px solid rgba(232,41,74,0.2)',
              borderRadius: 'var(--r-xl)', padding: '32px 28px',
              boxShadow: 'var(--shadow-card)',
            }}>
              <p style={{ fontSize: 14, color: 'var(--ink-2)', marginBottom: 20, lineHeight: 1.65 }}>{error}</p>
              <button className="btn btn-signal" onClick={handleRefresh}>Retry</button>
            </div>
          </div>
        )}

        {/* Dashboard */}
        {pipelineStatus.status === 'complete' && creator && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 40, animation: 'fadeUp 0.4s ease' }}>

            {/* Profile */}
            <ProfileCard creator={creator} metrics={creator.engagement_metrics} />

            {/* Metrics */}
            <div>
              <SectionLabel>Key metrics</SectionLabel>
              <MetricsSummary
                metrics={creator.engagement_metrics}
                classificationSummary={classificationSummary}
              />
            </div>

            {/* Posts */}
            <div>
              <SectionLabel>Recent posts — {posts.length} analyzed</SectionLabel>
              <PostGrid posts={posts} />
            </div>

            {/* Chart */}
            <div>
              <SectionLabel>Engagement per post</SectionLabel>
              <EngagementChart posts={posts} hideTitle />
            </div>

            {/* Hashtags */}
            {creator.engagement_metrics?.top_hashtag_list?.length > 0 && (
              <div>
                <SectionLabel>Top hashtags</SectionLabel>
                <HashtagCloud hashtags={creator.engagement_metrics.top_hashtag_list} hideTitle />
              </div>
            )}

            <Rule label="COMMENT INTELLIGENCE" />

            {/* Comment classification */}
            <div>
              <SectionLabel>Comment classification</SectionLabel>
              <CommentClassificationPanel summary={classificationSummary} />
            </div>

            <Rule label="AUDIENCE INTELLIGENCE" />

            {/* Audience */}
            <div>
              <SectionLabel>Audience intelligence</SectionLabel>
              <AudiencePanel audience={audience} />
            </div>

            {/* Footer note */}
            <div style={{
              fontFamily: 'var(--font-data)', fontSize: 11,
              color: 'var(--ink-4)', lineHeight: 1.8,
              padding: '16px 20px',
              background: 'var(--surface)', border: '1px solid var(--rule)',
              borderRadius: 'var(--r-md)',
              letterSpacing: '0.02em',
            }}>
              ER = (avg_likes + avg_comments + avg_saves) / follower_count × 100
              {'  '}·{'  '}
              Audience estimates derived from bio signals, hashtag analysis, and comment language distribution.
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
