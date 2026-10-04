import { useEffect, useMemo, useState } from 'react'
import { Link, NavLink, Route, Routes, useNavigate, useParams } from 'react-router-dom'
import './App.css'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

type ActionItem = {
  id: number
  description: string
  assignee: string
  deadline: string
  priority: string
  status: string
}

type Decision = {
  id: number
  decision: string
  context: string
  source_time: number
}

type MeetingSegment = {
  id: number
  speaker: string
  start_time: number
  end_time: number
  text: string
}

type Meeting = {
  id: number
  title: string
  original_filename: string
  file_type: string
  duration: number
  status: string
  created_at: string | null
  summary: string
  detailed_summary: string
  transcript: string
  sentiment: string
  topics: string[]
  action_items: ActionItem[]
  decisions: Decision[]
  questions: { id: number; question: string; answer: string }[]
  segments: MeetingSegment[]
}

type SearchResult = {
  speaker: string
  start_time: number
  end_time: number
  text: string
  score: number
}

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers: {
      ...(options?.headers ?? {}),
    },
  })

  if (!response.ok) {
    const errorText = await response.text()
    throw new Error(errorText || 'Request failed')
  }

  if (response.status === 204) {
    return undefined as T
  }

  return response.json() as Promise<T>
}

function formatDate(dateString: string | null) {
  if (!dateString) return 'Just now'

  return new Date(dateString).toLocaleString([], {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

function App() {
  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="container nav-wrap">
          <Link to="/" className="brand">
            <span className="brand-mark">M</span>
            MeetingMind
          </Link>

          <nav className="main-nav">
            <NavLink to="/">Home</NavLink>
            <NavLink to="/dashboard">Dashboard</NavLink>
          </nav>

          <Link to="/dashboard" className="button button-primary">
            Open workspace
          </Link>
        </div>
      </header>

      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/meetings/:meetingId" element={<MeetingDetailPage />} />
      </Routes>
    </div>
  )
}

function LandingPage() {
  return (
    <main>
      <section className="hero-section">
        <div className="container hero-grid">
          <div>
            <span className="eyebrow">AI meeting intelligence</span>
            <h1>Turn meetings into decisions, actions, and next steps.</h1>
            <p className="hero-copy">
              MeetingMind captures conversations, summarizes them with AI, detects commitments,
              and makes your team instantly searchable.
            </p>
            <div className="hero-actions">
              <Link to="/dashboard" className="button button-primary">
                Launch dashboard
              </Link>
              <a href="#features" className="button button-secondary">
                Explore features
              </a>
            </div>

            <div className="stat-row">
              <div>
                <strong>87%</strong>
                <span>faster follow-up</span>
              </div>
              <div>
                <strong>4.9/5</strong>
                <span>team satisfaction</span>
              </div>
              <div>
                <strong>1.2k</strong>
                <span>meetings processed</span>
              </div>
            </div>
          </div>

          <div className="hero-panel">
            <div className="mini-card">
              <span className="label">Executive summary</span>
              <h3>Launch plan aligned with marketing and product teams.</h3>
              <ul>
                <li>Decision: ship the beta in 2 weeks.</li>
                <li>Action: finalize launch checklist by Thursday.</li>
                <li>Theme: revenue expansion and onboarding readiness.</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      <section id="features" className="features-section">
        <div className="container">
          <div className="section-head">
            <span className="eyebrow">Built for execution</span>
            <h2>Everything your team needs after the call ends.</h2>
          </div>

          <div className="feature-grid">
            <article className="feature-card">
              <span className="feature-icon">🎙️</span>
              <h3>AI transcript capture</h3>
              <p>Upload recordings and let the platform transcribe, segment, and structure what was said.</p>
            </article>
            <article className="feature-card">
              <span className="feature-icon">✅</span>
              <h3>Action extraction</h3>
              <p>Spot owners, deadlines, and priorities automatically from the conversation context.</p>
            </article>
            <article className="feature-card">
              <span className="feature-icon">🧠</span>
              <h3>Semantic search</h3>
              <p>Ask questions about a meeting and retrieve the exact moments that support the answer.</p>
            </article>
            <article className="feature-card">
              <span className="feature-icon">📊</span>
              <h3>Decision tracking</h3>
              <p>Capture important commitments and maintain a searchable record for later follow-up.</p>
            </article>
          </div>
        </div>
      </section>
    </main>
  )
}

function DashboardPage() {
  const navigate = useNavigate()
  const [meetings, setMeetings] = useState<Meeting[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)

  const reloadMeetings = async () => {
    try {
      setLoading(true)
      const data = await fetchJson<Meeting[]>('/meetings')
      setMeetings(data)
      setError('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to load meetings')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void reloadMeetings()
  }, [])

  const handleUpload = async () => {
    if (!selectedFile) return

    const formData = new FormData()
    formData.append('file', selectedFile)

    try {
      const created = await fetchJson<Meeting>('/meetings/upload', {
        method: 'POST',
        body: formData,
      })
      setSelectedFile(null)
      await reloadMeetings()
      navigate(`/meetings/${created.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed')
    }
  }

  const handleDelete = async (meetingId: number) => {
    if (!window.confirm('Delete this meeting and all extracted data?')) return

    try {
      await fetchJson(`/meetings/${meetingId}`, { method: 'DELETE' })
      await reloadMeetings()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Delete failed')
    }
  }

  return (
    <main className="container dashboard-page">
      <section className="panel upload-panel">
        <div>
          <span className="eyebrow">New analysis</span>
          <h2>Upload a meeting recording</h2>
        </div>

        <div className="upload-row">
          <input
            type="file"
            accept="audio/*,video/*"
            onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)}
          />
          <button
            className="button button-primary"
            onClick={handleUpload}
            disabled={!selectedFile || loading}
          >
            Process meeting
          </button>
        </div>
      </section>

      {error && <div className="notice error">{error}</div>}

      <section className="dashboard-grid">
        <div className="stats-panel panel">
          <span className="eyebrow">Overview</span>
          <h3>Workspace metrics</h3>
          <div className="metric-grid">
            <div className="metric-box">
              <strong>{meetings.length}</strong>
              <span>meetings</span>
            </div>
            <div className="metric-box">
              <strong>{meetings.reduce((count, item) => count + item.action_items.length, 0)}</strong>
              <span>actions</span>
            </div>
            <div className="metric-box">
              <strong>{meetings.reduce((count, item) => count + item.decisions.length, 0)}</strong>
              <span>decisions</span>
            </div>
          </div>
        </div>

        <div className="history-panel panel">
          <div className="panel-header">
            <span className="eyebrow">Recent meetings</span>
            <h3>Meeting archive</h3>
          </div>

          {loading ? (
            <p className="muted">Loading meetings…</p>
          ) : meetings.length === 0 ? (
            <p className="muted">No meetings yet. Upload one to begin.</p>
          ) : (
            <div className="meeting-list">
              {meetings.map((meeting) => (
                <div key={meeting.id} className="meeting-card">
                  <div className="meeting-card-header">
                    <div>
                      <h4>{meeting.title}</h4>
                      <p>{formatDate(meeting.created_at)}</p>
                    </div>
                    <span className={`status-pill ${meeting.status}`}>{meeting.status}</span>
                  </div>

                  <p className="summary-preview">{meeting.summary || 'No summary generated yet.'}</p>

                  <div className="meeting-card-actions">
                    <button className="button button-secondary" onClick={() => navigate(`/meetings/${meeting.id}`)}>
                      Open
                    </button>
                    <button className="button ghost-button" onClick={() => handleDelete(meeting.id)}>
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>
    </main>
  )
}

function MeetingDetailPage() {
  const { meetingId } = useParams()
  const [meeting, setMeeting] = useState<Meeting | null>(null)
  const [loading, setLoading] = useState(true)
  const [query, setQuery] = useState('')
  const [searchResults, setSearchResults] = useState<SearchResult[]>([])
  const [answer, setAnswer] = useState('')
  const [sources, setSources] = useState<string[]>([])
  const [error, setError] = useState('')

  const loadMeeting = async () => {
    if (!meetingId) return

    try {
      setLoading(true)
      const data = await fetchJson<Meeting>(`/meetings/${meetingId}`)
      setMeeting(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Meeting not found')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadMeeting()
  }, [meetingId])

  const handleSearch = async () => {
    if (!meetingId || !query.trim()) return

    try {
      const data = await fetchJson<{ results: SearchResult[] }>(`/meetings/${meetingId}/search?q=${encodeURIComponent(query)}`)
      setSearchResults(data.results)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed')
    }
  }

  const handleAsk = async () => {
    if (!meetingId || !query.trim()) return

    try {
      const data = await fetchJson<{ answer: string; sources: string[] }>(`/meetings/${meetingId}/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: query }),
      })
      setAnswer(data.answer)
      setSources(data.sources)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Question failed')
    }
  }

  const updateActionStatus = async (actionItemId: number, status: string) => {
    try {
      await fetchJson(`/action-items/${actionItemId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status }),
      })
      await loadMeeting()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to update action')
    }
  }

  const exportMeeting = async (format: 'markdown' | 'json') => {
    if (!meetingId) return

    const data = await fetchJson<{ content: string; format: string }>(`/meetings/${meetingId}/export?format=${format}`)
    const blob = new Blob([data.content], { type: 'text/plain;charset=utf-8' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `${meeting?.title ?? 'meeting'}-summary.${format === 'json' ? 'json' : 'md'}`
    link.click()
    URL.revokeObjectURL(link.href)
  }

  const summaryText = useMemo(() => {
    if (!meeting) return ''
    return meeting.summary || 'No summary has been generated for this meeting yet.'
  }, [meeting])

  if (loading) return <main className="container page-spinner">Loading meeting…</main>
  if (error || !meeting) return <main className="container page-error">{error || 'Meeting not found'}</main>

  return (
    <main className="container detail-page">
      <section className="page-header panel">
        <div>
          <span className="eyebrow">Meeting detail</span>
          <h2>{meeting.title}</h2>
          <p className="muted">{formatDate(meeting.created_at)} • {meeting.status}</p>
        </div>

        <div className="header-actions">
          <button className="button button-secondary" onClick={() => void exportMeeting('markdown')}>
            Export Markdown
          </button>
          <button className="button button-secondary" onClick={() => void exportMeeting('json')}>
            Export JSON
          </button>
        </div>
      </section>

      <div className="detail-grid">
        <section className="panel summary-panel">
          <h3>Executive summary</h3>
          <p>{summaryText}</p>

          <div className="pill-row">
            {meeting.topics.map((topic) => (
              <span key={topic} className="tag-pill">
                {topic}
              </span>
            ))}
          </div>

          <div className="meta-box">
            <span>Sentiment</span>
            <strong>{meeting.sentiment}</strong>
          </div>
        </section>

        <section className="panel action-panel">
          <h3>Action items</h3>
          <div className="stack-list">
            {meeting.action_items.length === 0 ? (
              <p className="muted">No action items extracted yet.</p>
            ) : (
              meeting.action_items.map((item) => (
                <div key={item.id} className="stack-item">
                  <div className="stack-item__content">
                    <h4>{item.description}</h4>
                    <p>
                      {item.assignee} • {item.deadline} • {item.priority}
                    </p>
                  </div>

                  <select
                    value={item.status}
                    onChange={(event) => void updateActionStatus(item.id, event.target.value)}
                  >
                    <option value="open">Open</option>
                    <option value="in_progress">In progress</option>
                    <option value="done">Done</option>
                  </select>
                </div>
              ))
            )}
          </div>
        </section>
      </div>

      <section className="panel decision-panel">
        <h3>Key decisions</h3>
        <div className="decision-grid">
          {meeting.decisions.length === 0 ? (
            <p className="muted">No decisions extracted yet.</p>
          ) : (
            meeting.decisions.map((decision) => (
              <article key={decision.id} className="decision-card">
                <span className="eyebrow">Decision</span>
                <h4>{decision.decision}</h4>
                <p>{decision.context}</p>
              </article>
            ))
          )}
        </div>
      </section>

      <section className="panel ai-panel">
        <div className="panel-header">
          <h3>Ask the meeting</h3>
        </div>

        <div className="search-row">
          <input
            type="text"
            placeholder="Ask about timeline, owners, blockers, or risks"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
          <button className="button button-primary" onClick={() => void handleSearch()}>
            Search transcript
          </button>
          <button className="button button-secondary" onClick={() => void handleAsk()}>
            Ask AI
          </button>
        </div>

        {searchResults.length > 0 && (
          <div className="result-box">
            <h4>Semantic matches</h4>
            <ul>
              {searchResults.map((result, index) => (
                <li key={`${result.speaker}-${index}`}>
                  <strong>{result.speaker}</strong> • {result.start_time}s
                  <p>{result.text}</p>
                </li>
              ))}
            </ul>
          </div>
        )}

        {answer && (
          <div className="answer-box">
            <h4>Answer</h4>
            <p>{answer}</p>
            {sources.length > 0 && (
              <div className="source-list">
                <strong>Sources:</strong>
                {sources.map((source, index) => (
                  <span key={`${source}-${index}`}>{source}</span>
                ))}
              </div>
            )}
          </div>
        )}
      </section>

      <section className="panel transcript-panel">
        <h3>Transcript</h3>
        <div className="transcript-list">
          {meeting.segments.length === 0 ? (
            <p className="muted">No transcript segments available.</p>
          ) : (
            meeting.segments.map((segment) => (
              <div key={segment.id} className="transcript-item">
                <span className="speaker-badge">{segment.speaker}</span>
                <time>{segment.start_time.toFixed(1)}s</time>
                <p>{segment.text}</p>
              </div>
            ))
          )}
        </div>
      </section>
    </main>
  )
}

export default App