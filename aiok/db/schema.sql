-- ============================================
-- AIOK Database Schema
-- 업무자동화 AI Agent 오케스트레이션 시스템
-- 생성일: 2026-03-23
-- ============================================

-- 데이터베이스 생성 (필요시 주석 해제)
-- CREATE DATABASE aiok;

-- 확장 설치
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- 향후 RAG 확장 시: CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================
-- 1. users (사용자)
-- ============================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100),

    role VARCHAR(20) DEFAULT 'user',
    department VARCHAR(100),

    timezone VARCHAR(50) DEFAULT 'Asia/Seoul',
    language VARCHAR(10) DEFAULT 'ko',

    is_active BOOLEAN DEFAULT TRUE,
    preferences JSONB DEFAULT '{}',

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_department ON users(department);

-- ============================================
-- 2. sessions (세션)
-- ============================================
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,

    context JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_active_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_last_active ON sessions(last_active_at);

-- ============================================
-- 3. conversations (대화 기록)
-- ============================================
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    turn_number INTEGER NOT NULL,

    user_message TEXT NOT NULL,

    intent VARCHAR(50),
    confidence FLOAT,
    agent_used VARCHAR(50),

    response_type VARCHAR(50),
    agent_response JSONB NOT NULL,

    tokens_used INTEGER,
    processing_time_ms INTEGER,
    feedback VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,

    UNIQUE(session_id, turn_number)
);

CREATE INDEX idx_conversations_session ON conversations(session_id);
CREATE INDEX idx_conversations_intent ON conversations(intent);
CREATE INDEX idx_conversations_created ON conversations(created_at);

-- ============================================
-- 4. oauth_tokens (OAuth 토큰)
-- ============================================
CREATE TABLE oauth_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,

    provider VARCHAR(20) NOT NULL,
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    token_type VARCHAR(20) DEFAULT 'Bearer',

    scopes TEXT[],
    expires_at TIMESTAMPTZ NOT NULL,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(user_id, provider)
);

CREATE INDEX idx_oauth_tokens_user ON oauth_tokens(user_id);

-- ============================================
-- 5. translation_cache (번역 캐시)
-- ============================================
CREATE TABLE translation_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    source_text_hash VARCHAR(64) NOT NULL,
    source_text TEXT NOT NULL,
    source_lang VARCHAR(10),
    target_lang VARCHAR(10) NOT NULL,
    style VARCHAR(20),

    translated_text TEXT NOT NULL,

    hit_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(source_text_hash, target_lang, style)
);

CREATE INDEX idx_translation_hash ON translation_cache(source_text_hash);

-- ============================================
-- 6. calendar_events_cache (캘린더 캐시)
-- ============================================
CREATE TABLE calendar_events_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,

    google_event_id VARCHAR(255) UNIQUE,
    title VARCHAR(500),
    description TEXT,

    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NOT NULL,
    location VARCHAR(500),
    attendees JSONB DEFAULT '[]',

    raw_data JSONB,
    synced_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_calendar_user ON calendar_events_cache(user_id);
CREATE INDEX idx_calendar_time ON calendar_events_cache(start_time, end_time);

-- ============================================
-- 7. agent_logs (에이전트 로그)
-- ============================================
CREATE TABLE agent_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    session_id UUID REFERENCES sessions(id) ON DELETE SET NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,

    agent_type VARCHAR(50) NOT NULL,
    action VARCHAR(100),

    input_summary TEXT,
    output_summary TEXT,

    processing_time_ms INTEGER,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_agent_logs_agent ON agent_logs(agent_type);
CREATE INDEX idx_agent_logs_created ON agent_logs(created_at);

-- ============================================
-- 8. documents (문서 - RAG 확장 대비)
-- ============================================
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,

    title VARCHAR(500),
    content TEXT NOT NULL,
    doc_type VARCHAR(50),
    source VARCHAR(255),

    embedding_status VARCHAR(20) DEFAULT 'pending',

    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_documents_user ON documents(user_id);
CREATE INDEX idx_documents_type ON documents(doc_type);
CREATE INDEX idx_documents_embedding_status ON documents(embedding_status);
