-- Initialize Real Estate Wholesale Business Database
-- This script creates the database and initial user

-- Create database (if not exists)
-- Note: This is typically done by the POSTGRES_DB environment variable

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create initial admin user (password: admin123)
-- This will be created by the application on first run
-- You can also create it manually here if needed

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE real_estate_db TO real_estate_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO real_estate_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO real_estate_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO real_estate_user;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO real_estate_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO real_estate_user; 