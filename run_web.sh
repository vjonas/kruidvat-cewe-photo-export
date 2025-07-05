#!/bin/bash

# CEWE Photo Book Fetcher Runner Script (Web Interface Version)
# This version runs non-interactively and defaults to fetching all pages

echo "🔧 Setting up CEWE Photo Book Fetcher..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Test URL structure first
echo "🧪 Testing URL structure..."
python test_url.py

echo ""
echo "🚀 Starting photo book fetch..."
echo "📸 Fetching all pages (1-98)..."
echo ""

# Run the photo book fetcher with default settings (all pages)
python fetch_photobook.py

echo ""
echo "✅ Done! Check the output/ directory for your PDF."