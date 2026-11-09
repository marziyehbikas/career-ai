ALTER TABLE resume_analyses
ADD COLUMN IF NOT EXISTS resume_text_snapshot TEXT,
ADD COLUMN IF NOT EXISTS content_hash VARCHAR(64);