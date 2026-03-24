import { useState, useEffect } from 'react';
import './LogPanel.css';

interface LogEntry {
  timestamp: string;
  type: 'agent' | 'tool' | 'info' | 'error';
  message: string;
}

interface LogPanelProps {
  sessionId: string | null;
  isCollapsed: boolean;
  onToggle: () => void;
}

export function LogPanel({ sessionId, isCollapsed, onToggle }: LogPanelProps) {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [activeTab, setActiveTab] = useState<'logs' | 'session'>('logs');
  const [sessionData, setSessionData] = useState<any>(null);

  // Poll for logs (in real implementation, use WebSocket or SSE)
  useEffect(() => {
    if (!sessionId) return;

    const fetchSessionData = async () => {
      try {
        const response = await fetch(
          `http://localhost:8000/api/v1/sessions/${sessionId}/messages?user_id=default_user`
        );
        if (response.ok) {
          const data = await response.json();
          setSessionData(data);
        }
      } catch (error) {
        console.error('Failed to fetch session data:', error);
      }
    };

    fetchSessionData();
    const interval = setInterval(fetchSessionData, 3000);
    return () => clearInterval(interval);
  }, [sessionId]);

  const addLog = (type: LogEntry['type'], message: string) => {
    const entry: LogEntry = {
      timestamp: new Date().toLocaleTimeString(),
      type,
      message,
    };
    setLogs(prev => [...prev.slice(-50), entry]); // Keep last 50 logs
  };

  // Expose addLog globally for debugging
  useEffect(() => {
    (window as any).addLog = addLog;
  }, []);

  if (isCollapsed) {
    return (
      <div className="log-panel collapsed">
        <button className="toggle-btn" onClick={onToggle}>
          &lt;
        </button>
      </div>
    );
  }

  return (
    <div className="log-panel">
      <div className="log-header">
        <div className="tabs">
          <button
            className={`tab ${activeTab === 'logs' ? 'active' : ''}`}
            onClick={() => setActiveTab('logs')}
          >
            Logs
          </button>
          <button
            className={`tab ${activeTab === 'session' ? 'active' : ''}`}
            onClick={() => setActiveTab('session')}
          >
            Session
          </button>
        </div>
        <button className="toggle-btn" onClick={onToggle}>
          &gt;
        </button>
      </div>

      <div className="log-content">
        {activeTab === 'logs' ? (
          <div className="logs-view">
            {logs.length === 0 ? (
              <div className="empty-state">No logs yet</div>
            ) : (
              logs.map((log, index) => (
                <div key={index} className={`log-entry ${log.type}`}>
                  <span className="log-time">{log.timestamp}</span>
                  <span className={`log-type ${log.type}`}>{log.type}</span>
                  <span className="log-message">{log.message}</span>
                </div>
              ))
            )}
          </div>
        ) : (
          <div className="session-view">
            {!sessionId ? (
              <div className="empty-state">No active session</div>
            ) : (
              <>
                <div className="session-info">
                  <strong>Session ID:</strong>
                  <code>{sessionId.slice(0, 8)}...</code>
                </div>
                {sessionData && (
                  <div className="session-messages">
                    <strong>Messages ({sessionData.messages?.length || 0}):</strong>
                    <div className="messages-list">
                      {sessionData.messages?.map((msg: any, idx: number) => (
                        <div key={idx} className={`session-msg ${msg.role}`}>
                          <span className="role">{msg.role}</span>
                          <span className="content">
                            {msg.content.slice(0, 100)}
                            {msg.content.length > 100 ? '...' : ''}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
