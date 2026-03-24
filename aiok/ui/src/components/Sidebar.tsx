import { useEffect, useState } from 'react'
import './Sidebar.css'

interface Session {
  session_id: string
  user_id: string
  created_at: string | null
  last_message: string | null
}

interface SidebarProps {
  currentSessionId: string | null
  onSessionSelect: (sessionId: string | null) => void
  onNewChat: () => void
}

export function Sidebar({ currentSessionId, onSessionSelect, onNewChat }: SidebarProps) {
  const [sessions, setSessions] = useState<Session[]>([])
  const [isCollapsed, setIsCollapsed] = useState(false)

  const fetchSessions = async () => {
    try {
      const response = await fetch('/api/v1/sessions')
      if (response.ok) {
        const data = await response.json()
        setSessions(data)
      }
    } catch (error) {
      console.error('Failed to fetch sessions:', error)
    }
  }

  useEffect(() => {
    fetchSessions()
    // 주기적으로 세션 목록 갱신
    const interval = setInterval(fetchSessions, 5000)
    return () => clearInterval(interval)
  }, [])

  // 새 세션 생성시 목록 갱신
  useEffect(() => {
    if (currentSessionId) {
      fetchSessions()
    }
  }, [currentSessionId])

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return ''
    const date = new Date(dateStr)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const days = Math.floor(diff / (1000 * 60 * 60 * 24))

    if (days === 0) {
      return date.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })
    } else if (days === 1) {
      return '어제'
    } else if (days < 7) {
      return `${days}일 전`
    } else {
      return date.toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' })
    }
  }

  return (
    <aside className={`sidebar ${isCollapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        <button className="toggle-btn" onClick={() => setIsCollapsed(!isCollapsed)}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            {isCollapsed ? (
              <path d="M9 18l6-6-6-6" />
            ) : (
              <path d="M15 18l-6-6 6-6" />
            )}
          </svg>
        </button>
        {!isCollapsed && <span className="sidebar-title">Sessions</span>}
      </div>

      <button className="new-chat-btn" onClick={onNewChat}>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M12 5v14M5 12h14" />
        </svg>
        {!isCollapsed && <span>New Chat</span>}
      </button>

      {!isCollapsed && (
        <div className="sessions-list">
          {sessions.length === 0 ? (
            <div className="empty-sessions">
              <p>No sessions yet</p>
            </div>
          ) : (
            sessions.map((session) => (
              <button
                key={session.session_id}
                className={`session-item ${currentSessionId === session.session_id ? 'active' : ''}`}
                onClick={() => onSessionSelect(session.session_id)}
              >
                <div className="session-icon">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                  </svg>
                </div>
                <div className="session-info">
                  <span className="session-preview">
                    {session.last_message || 'New conversation'}
                  </span>
                  <span className="session-time">
                    {formatDate(session.created_at)}
                  </span>
                </div>
              </button>
            ))
          )}
        </div>
      )}
    </aside>
  )
}
