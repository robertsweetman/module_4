-- eTenders Database Schema
-- Complete schema for all 7 tables with relationships

-- Drop tables if they exist (in correct order due to foreign keys)
DROP TABLE IF EXISTS tender_notification CASCADE;
DROP TABLE IF EXISTS bid_submission CASCADE;
DROP TABLE IF EXISTS sales_updates CASCADE;
DROP TABLE IF EXISTS cpv_checker CASCADE;
DROP TABLE IF EXISTS bid_analysis CASCADE;
DROP TABLE IF EXISTS etenders_pdf CASCADE;
DROP TABLE IF EXISTS etenders_core CASCADE;

-- 1. ETENDERS_CORE - Main tender data
CREATE TABLE etenders_core (
    resource_id VARCHAR(50) PRIMARY KEY,
    row_number INTEGER,
    title TEXT NOT NULL,
    detail_url TEXT,
    contracting_authority TEXT,
    info TEXT,
    date_published TEXT,  -- Raw scraped date string
    submission_deadline TEXT,  -- Raw scraped deadline string
    procedure VARCHAR(100),
    status VARCHAR(50),
    notice_pdf_url TEXT,
    award_date TEXT,  -- Raw scraped award date string
    estimated_value VARCHAR(50),
    cycle INTEGER,
    date_published_parsed TIMESTAMP,  -- Parsed and validated date
    submission_deadline_parsed TIMESTAMP,  -- Parsed and validated deadline
    award_date_parsed TIMESTAMP,  -- Parsed and validated award date
    estimated_value_numeric DECIMAL(15,2),
    cycle_numeric INTEGER,
    has_pdf_url BOOLEAN DEFAULT FALSE,
    has_estimated_value BOOLEAN DEFAULT FALSE,
    is_open BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. ETENDERS_PDF - PDF content data
CREATE TABLE etenders_pdf (
    resource_id VARCHAR(50) PRIMARY KEY REFERENCES etenders_core(resource_id) ON DELETE CASCADE,
    pdf_url TEXT,
    pdf_parsed BOOLEAN DEFAULT FALSE,
    pdf_content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. BID_ANALYSIS - AI-generated bid recommendations
CREATE TABLE bid_analysis (
    resource_id VARCHAR(50) PRIMARY KEY REFERENCES etenders_core(resource_id) ON DELETE CASCADE,
    should_bid BOOLEAN,
    confidence DECIMAL(3,2),
    reasoning TEXT,
    relevant_factors TEXT,
    estimated_fit DECIMAL(3,2),
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. CPV_CHECKER - CPV code validation
CREATE TABLE cpv_checker (
    resource_id VARCHAR(50) PRIMARY KEY REFERENCES etenders_core(resource_id) ON DELETE CASCADE,
    cpv_count INTEGER DEFAULT 0,
    cpv_codes JSONB,
    cpv_details JSONB,
    has_validated_cpv BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. SALES_UPDATES - Sales team progress updates
CREATE TABLE sales_updates (
    id SERIAL PRIMARY KEY,
    resource_id VARCHAR(50) REFERENCES etenders_core(resource_id) ON DELETE CASCADE,
    update_date DATE NOT NULL,
    sales_comment TEXT,
    author VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. BID_SUBMISSION - Submitted bids tracking
CREATE TABLE bid_submission (
    resource_id VARCHAR(50) PRIMARY KEY REFERENCES etenders_core(resource_id) ON DELETE CASCADE,
    submission_date DATE NOT NULL,
    bid_document TEXT,
    author VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. TENDER_NOTIFICATION - Award notifications
CREATE TABLE tender_notification (
    resource_id VARCHAR(50) PRIMARY KEY REFERENCES etenders_core(resource_id) ON DELETE CASCADE,
    notification_date DATE NOT NULL,
    winning_bidder TEXT,
    bid_terms TEXT,
    award_reasons TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for common queries
CREATE INDEX idx_etenders_core_published ON etenders_core(date_published_parsed DESC);
CREATE INDEX idx_etenders_core_deadline ON etenders_core(submission_deadline_parsed);
CREATE INDEX idx_etenders_core_status ON etenders_core(status);
CREATE INDEX idx_etenders_core_value ON etenders_core(estimated_value_numeric);
CREATE INDEX idx_cpv_checker_validated ON cpv_checker(has_validated_cpv);
CREATE INDEX idx_sales_updates_resource ON sales_updates(resource_id);
CREATE INDEX idx_sales_updates_date ON sales_updates(update_date DESC);

-- Create update trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add update triggers to all tables
CREATE TRIGGER update_etenders_core_updated_at BEFORE UPDATE ON etenders_core
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_etenders_pdf_updated_at BEFORE UPDATE ON etenders_pdf
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bid_analysis_updated_at BEFORE UPDATE ON bid_analysis
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cpv_checker_updated_at BEFORE UPDATE ON cpv_checker
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sales_updates_updated_at BEFORE UPDATE ON sales_updates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bid_submission_updated_at BEFORE UPDATE ON bid_submission
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tender_notification_updated_at BEFORE UPDATE ON tender_notification
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO etenders_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO etenders_user;

-- Print confirmation
DO $$
BEGIN
    RAISE NOTICE 'Schema created successfully with % tables', (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public');
END $$;
