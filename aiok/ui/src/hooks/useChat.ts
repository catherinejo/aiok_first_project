import { useState, useCallback, useEffect } from 'react'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  files?: UploadedFile[]
}

interface ChatResponse {
  session_id: string
  response: string
}

export interface UploadedFile {
  file_id: string
  filename: string
  content_preview: string
  char_count: number
}

interface UseChatOptions {
  initialSessionId?: string | null
  onSessionChange?: (sessionId: string) => void
}

export function useChat(options: UseChatOptions = {}) {
  const [messages, setMessages] = useState<Message[]>([])
  const [sessionId, setSessionId] = useState<string | null>(options.initialSessionId ?? null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [pendingFiles, setPendingFiles] = useState<UploadedFile[]>([])

  // 외부에서 세션 ID 변경 시 히스토리 로드 또는 초기화
  useEffect(() => {
    if (options.initialSessionId !== undefined && options.initialSessionId !== sessionId) {
      setSessionId(options.initialSessionId)
      setError(null)
      setPendingFiles([])

      // 기존 세션이면 히스토리 로드, 새 세션이면 초기화
      if (options.initialSessionId) {
        loadSessionHistory(options.initialSessionId)
      } else {
        setMessages([])
      }
    }
  }, [options.initialSessionId])

  const loadSessionHistory = async (sid: string) => {
    try {
      const response = await fetch(`/api/v1/sessions/${sid}/messages`)
      if (response.ok) {
        const data = await response.json()
        const loadedMessages: Message[] = data.messages.map((msg: { role: string; content: string }, index: number) => ({
          id: `${sid}-${index}`,
          role: msg.role as 'user' | 'assistant',
          content: msg.content,
          timestamp: new Date(),
        }))
        setMessages(loadedMessages)
      } else {
        setMessages([])
      }
    } catch {
      setMessages([])
    }
  }

  const uploadFile = useCallback(async (file: File): Promise<UploadedFile | null> => {
    const formData = new FormData()
    formData.append('file', file)
    if (sessionId) {
      formData.append('session_id', sessionId)
    }

    try {
      const response = await fetch('/api/v1/upload', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || `HTTP ${response.status}`)
      }

      const data: UploadedFile = await response.json()
      setPendingFiles((prev) => [...prev, data])
      return data
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed')
      return null
    }
  }, [sessionId])

  const removeFile = useCallback((fileId: string) => {
    setPendingFiles((prev) => prev.filter((f) => f.file_id !== fileId))
  }, [])

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim() && pendingFiles.length === 0) return

    const fileIds = pendingFiles.map((f) => f.file_id)
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content,
      timestamp: new Date(),
      files: pendingFiles.length > 0 ? [...pendingFiles] : undefined,
    }

    setMessages((prev) => [...prev, userMessage])
    setPendingFiles([])
    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch('/api/v1/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: content,
          session_id: sessionId,
          file_ids: fileIds.length > 0 ? fileIds : undefined,
        }),
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      const data: ChatResponse = await response.json()

      if (!sessionId) {
        setSessionId(data.session_id)
        options.onSessionChange?.(data.session_id)
      }

      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: data.response,
        timestamp: new Date(),
      }

      setMessages((prev) => [...prev, assistantMessage])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setIsLoading(false)
    }
  }, [sessionId, pendingFiles, options])

  const clearChat = useCallback(() => {
    setMessages([])
    setSessionId(null)
    setError(null)
    setPendingFiles([])
  }, [])

  return {
    messages,
    sessionId,
    isLoading,
    error,
    pendingFiles,
    sendMessage,
    uploadFile,
    removeFile,
    clearChat,
  }
}
