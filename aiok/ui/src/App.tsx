import { useState } from 'react'
import { Chat } from './components/Chat'
import { Sidebar } from './components/Sidebar'
import './App.css'

function App() {
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null)

  const handleSessionSelect = (sessionId: string | null) => {
    setCurrentSessionId(sessionId)
  }

  const handleNewChat = () => {
    setCurrentSessionId(null)
  }

  const handleSessionChange = (sessionId: string) => {
    setCurrentSessionId(sessionId)
  }

  return (
    <div className="app-layout">
      <Sidebar
        currentSessionId={currentSessionId}
        onSessionSelect={handleSessionSelect}
        onNewChat={handleNewChat}
      />
      <Chat
        sessionId={currentSessionId}
        onSessionChange={handleSessionChange}
      />
    </div>
  )
}

export default App
