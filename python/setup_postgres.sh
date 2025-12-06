#!/bin/bash
# Setup PostgreSQL for eTenders Data Product

set -e  # Exit on error

echo "🗄️  eTenders PostgreSQL Setup"
echo "================================"

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is not installed."
    echo ""
    echo "Install with Homebrew:"
    echo "  brew install postgresql@16"
    echo "  brew services start postgresql@16"
    exit 1
fi

echo "✓ PostgreSQL is installed"

# Check if PostgreSQL is running
if ! pg_isready > /dev/null 2>&1; then
    echo "⚠️  PostgreSQL is not running. Starting it..."
    brew services start postgresql@16
    sleep 3
    
    if ! pg_isready > /dev/null 2>&1; then
        echo "❌ Failed to start PostgreSQL"
        echo "Try manually: brew services start postgresql@16"
        exit 1
    fi
fi

echo "✓ PostgreSQL is running"

# Check if database exists
if psql -lqt | cut -d \| -f 1 | grep -qw etenders_db; then
    echo "⚠️  Database 'etenders_db' already exists"
    read -p "Do you want to drop it and start fresh? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Dropping existing database..."
        dropdb etenders_db 2>/dev/null || true
    else
        echo "Using existing database..."
    fi
fi

# Create database if it doesn't exist
if ! psql -lqt | cut -d \| -f 1 | grep -qw etenders_db; then
    echo "Creating database..."
    createdb etenders_db
    echo "✓ Database created"
fi

# Create user if doesn't exist
if ! psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='etenders_user'" | grep -q 1; then
    echo "Creating user..."
    psql etenders_db -c "CREATE USER etenders_user WITH PASSWORD 'etenders_pass';"
    echo "✓ User created"
else
    echo "✓ User already exists"
fi

# Grant privileges
echo "Granting privileges..."
psql etenders_db -c "GRANT ALL PRIVILEGES ON DATABASE etenders_db TO etenders_user;"
psql etenders_db -c "ALTER DATABASE etenders_db OWNER TO etenders_user;"

# Create schema
echo "Creating database schema..."
psql -U etenders_user -d etenders_db -f create_schema.sql

if [ $? -eq 0 ]; then
    echo "✓ Database schema created successfully"
else
    echo "❌ Failed to create schema"
    exit 1
fi

# Verify tables
echo ""
echo "Verifying tables created:"
psql -U etenders_user -d etenders_db -c "\dt"

echo ""
echo "================================"
echo "✅ PostgreSQL setup complete!"
echo ""
echo "Connection details (also in .env file):"
echo "  Host:     localhost"
echo "  Port:     5432"
echo "  Database: etenders_db"
echo "  User:     etenders_user"
echo "  Password: etenders_pass"
echo ""
echo "Database is ready with empty tables."
echo ""
echo "Next steps:"
echo "  Test:     python3 test_postgres_connection.py"
echo "  Run ETL:  python3 main.py"
echo ""
echo "Useful commands:"
echo "  Start:    brew services start postgresql@16"
echo "  Stop:     brew services stop postgresql@16"
echo "  Connect:  psql -U etenders_user -d etenders_db"
echo "  Status:   brew services list | grep postgres"
echo ""
