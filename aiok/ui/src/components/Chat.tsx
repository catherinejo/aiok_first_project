import { useState, useRef, useEffect, type FormEvent, type KeyboardEvent, type ChangeEvent } from 'react'
import { useChat } from '../hooks/useChat'
import './Chat.css'

interface ChatProps {
  sessionId: string | null
  onSessionChange: (sessionId: string) => void
}

const SUPPORTED_TYPES = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.presentationml.presentation',
  'application/vnd.ms-powerpoint',
]

export function Chat({ sessionId, onSessionChange }: ChatProps) {
  const { messages, isLoading, error, pendingFiles, sendMessage, uploadFile, removeFile, clearChat } = useChat({
    initialSessionId: sessionId,
    onSessionChange,
  })
  const [input, setInput] = useState('')
  const [isUploading, setIsUploading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // 답변 완료 후 input에 focus
  useEffect(() => {
    if (!isLoading && textareaRef.current) {
      textareaRef.current.focus()
    }
  }, [isLoading])

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    if ((input.trim() || pendingFiles.length > 0) && !isLoading) {
      sendMessage(input)
      setInput('')
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto'
      }
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value)
    // Auto-resize textarea
    e.target.style.height = 'auto'
    e.target.style.height = `${Math.min(e.target.scrollHeight, 200)}px`
  }

  const handleFileSelect = async (e: ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (!files || files.length === 0) return

    setIsUploading(true)
    for (const file of Array.from(files)) {
      if (!SUPPORTED_TYPES.includes(file.type)) {
        continue
      }
      await uploadFile(file)
    }
    setIsUploading(false)

    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const getFileIcon = (filename: string) => {
    const ext = filename.split('.').pop()?.toLowerCase()
    switch (ext) {
      case 'pdf':
        return '📄'
      case 'doc':
      case 'docx':
        return '📝'
      case 'ppt':
      case 'pptx':
        return '📊'
      default:
        return '📎'
    }
  }

  return (
    <div className="chat-container">
      <header className="chat-header">
        <h1>AIOK</h1>
        <span className="chat-subtitle">AI Orchestration for Work</span>
        <button className="clear-btn" onClick={clearChat} title="새 대화">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 5v14M5 12h14" />
          </svg>
        </button>
      </header>

      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="welcome">
            <h2>AIOK에 오신 것을 환영합니다</h2>
            <p>업무 자동화를 위한 AI 어시스턴트입니다.</p>
            <div className="features">
              <div className="feature">
                <span className="feature-icon">🌐</span>
                <span>통번역</span>
              </div>
              <div className="feature">
                <span className="feature-icon">📧</span>
                <span>메일 처리</span>
              </div>
              <div className="feature">
                <span className="feature-icon">📝</span>
                <span>회의록 정리</span>
              </div>
              <div className="feature">
                <span className="feature-icon">📅</span>
                <span>일정 관리</span>
              </div>
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <div key={message.id} className={`message ${message.role}`}>
              <div className="message-avatar">
                {message.role === 'user' ? '👤' : '🤖'}
              </div>
              <div className="message-content">
                {message.files && message.files.length > 0 && (
                  <div className="message-files">
                    {message.files.map((file) => (
                      <div key={file.file_id} className="file-badge">
                        <span>{getFileIcon(file.filename)}</span>
                        <span className="file-name">{file.filename}</span>
                      </div>
                    ))}
                  </div>
                )}
                <div className="message-text">{message.content}</div>
                <div className="message-time">
                  {message.timestamp.toLocaleTimeString('ko-KR', {
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </div>
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="message assistant">
            <div className="message-avatar">🤖</div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        {error && (
          <div className="error-message">
            오류가 발생했습니다: {error}
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-area">
        {pendingFiles.length > 0 && (
          <div className="pending-files">
            {pendingFiles.map((file) => (
              <div key={file.file_id} className="pending-file">
                <span>{getFileIcon(file.filename)}</span>
                <span className="file-name">{file.filename}</span>
                <span className="file-size">{Math.round(file.char_count / 1000)}K chars</span>
                <button
                  type="button"
                  className="remove-file-btn"
                  onClick={() => removeFile(file.file_id)}
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M18 6L6 18M6 6l12 12" />
                  </svg>
                </button>
              </div>
            ))}
          </div>
        )}
        <form className="input-form" onSubmit={handleSubmit}>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.doc,.docx,.ppt,.pptx"
            multiple
            onChange={handleFileSelect}
            style={{ display: 'none' }}
          />
          <button
            type="button"
            className="attach-btn"
            onClick={() => fileInputRef.current?.click()}
            disabled={isLoading || isUploading}
            title="파일 첨부 (PDF, Word, PPT)"
          >
            {isUploading ? (
              <div className="upload-spinner" />
            ) : (
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48" />
              </svg>
            )}
          </button>
          <textarea
            ref={textareaRef}
            value={input}
            onChange={handleTextareaChange}
            onKeyDown={handleKeyDown}
            placeholder="메시지를 입력하세요... (Shift+Enter로 줄바꿈)"
            disabled={isLoading}
            rows={1}
          />
          <button type="submit" disabled={(!input.trim() && pendingFiles.length === 0) || isLoading}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" />
            </svg>
          </button>
        </form>
      </div>
    </div>
  )
}
