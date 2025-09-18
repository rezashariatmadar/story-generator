#!/bin/bash
set -e

echo "🚀 Starting build process..."

# Check if we're running on Railway
if [ "$RAILWAY_ENVIRONMENT" != "" ]; then
    echo "📦 Running on Railway environment: $RAILWAY_ENVIRONMENT"
fi

# Check Python version
echo "🐍 Python version:"
python --version

# Upgrade pip to latest version
echo "⬆️ Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies with explicit flags
echo "📥 Installing dependencies from requirements.txt..."
pip install -r requirements.txt --no-cache-dir --disable-pip-version-check

# Verify gunicorn installation specifically
echo "🔍 Verifying gunicorn installation..."
which gunicorn || echo "⚠️ gunicorn not found in PATH"
gunicorn --version || echo "⚠️ gunicorn version check failed"

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "✅ Build process completed successfully!" 