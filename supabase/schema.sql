-- YouTube Productivity MVP Database Schema
-- This file creates the initial database schema for the YouTube Productivity application

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create videos table
CREATE TABLE videos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    youtube_id TEXT NOT NULL,
    title TEXT,
    duration INTEGER, -- Duration in seconds
    thumbnail TEXT,
    status TEXT DEFAULT 'pending', -- pending, processing, completed, failed
    job_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create transcripts table
CREATE TABLE transcripts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id UUID REFERENCES videos(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    language TEXT DEFAULT 'en',
    length_tokens INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create summaries table
CREATE TABLE summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id UUID REFERENCES videos(id) ON DELETE CASCADE,
    short_summary TEXT,
    long_summary TEXT,
    keywords JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create jobs table
CREATE TABLE jobs (
    id TEXT PRIMARY KEY,
    video_id UUID REFERENCES videos(id) ON DELETE SET NULL,
    status TEXT DEFAULT 'pending', -- pending, running, completed, failed
    progress INTEGER DEFAULT 0, -- Progress percentage (0-100)
    result JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_videos_user_id ON videos(user_id);
CREATE INDEX idx_videos_youtube_id ON videos(youtube_id);
CREATE INDEX idx_videos_status ON videos(status);
CREATE INDEX idx_transcripts_video_id ON transcripts(video_id);
CREATE INDEX idx_summaries_video_id ON summaries(video_id);
CREATE INDEX idx_jobs_video_id ON jobs(video_id);
CREATE INDEX idx_jobs_status ON jobs(status);

-- Create a function to update the updated_at timestamp (useful for future use)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add updated_at columns to tables that might need them in the future
ALTER TABLE users ADD COLUMN updated_at TIMESTAMPTZ DEFAULT NOW();
ALTER TABLE videos ADD COLUMN updated_at TIMESTAMPTZ DEFAULT NOW();
ALTER TABLE transcripts ADD COLUMN updated_at TIMESTAMPTZ DEFAULT NOW();
ALTER TABLE summaries ADD COLUMN updated_at TIMESTAMPTZ DEFAULT NOW();
ALTER TABLE jobs ADD COLUMN updated_at TIMESTAMPTZ DEFAULT NOW();

-- Create triggers to automatically update updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_videos_updated_at BEFORE UPDATE ON videos FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_transcripts_updated_at BEFORE UPDATE ON transcripts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_summaries_updated_at BEFORE UPDATE ON summaries FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_jobs_updated_at BEFORE UPDATE ON jobs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert some sample data for development (optional - remove in production)
INSERT INTO users (email) VALUES 
    ('test@example.com'),
    ('demo@example.com');

-- Add comments for documentation
COMMENT ON TABLE users IS 'User accounts for the YouTube Productivity application';
COMMENT ON TABLE videos IS 'YouTube videos being processed by users';
COMMENT ON TABLE transcripts IS 'Video transcripts extracted from YouTube videos';
COMMENT ON TABLE summaries IS 'AI-generated summaries of video content';
COMMENT ON TABLE jobs IS 'Background job tracking for video processing tasks';

COMMENT ON COLUMN videos.youtube_id IS 'YouTube video ID (e.g., from URL: youtube.com/watch?v=VIDEO_ID)';
COMMENT ON COLUMN videos.duration IS 'Video duration in seconds';
COMMENT ON COLUMN videos.status IS 'Processing status: pending, processing, completed, failed';
COMMENT ON COLUMN transcripts.language IS 'Language code of the transcript (ISO 639-1)';
COMMENT ON COLUMN transcripts.length_tokens IS 'Number of tokens in the transcript text';
COMMENT ON COLUMN summaries.keywords IS 'JSON array of extracted keywords from the video';
COMMENT ON COLUMN jobs.progress IS 'Job progress percentage (0-100)';
COMMENT ON COLUMN jobs.result IS 'JSON object containing job results or error information';
