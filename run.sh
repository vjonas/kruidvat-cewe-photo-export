#!/bin/bash

# CEWE Photo Book Fetcher Runner Script

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
echo "🚀 Ready to fetch photo book!"
echo ""
echo "Options:"
echo "  1. Fetch all pages (1-98) - Default"
echo "  2. Fetch specific page range"
echo "  3. Exit"
echo ""

read -p "Choose an option (1-3): " choice

case $choice in
    1)
        echo "📸 Fetching all pages (1-98)..."
        python fetch_photobook.py
        ;;
    2)
        read -p "Enter start page: " start_page
        read -p "Enter end page: " end_page
        echo "📸 Fetching pages $start_page to $end_page..."
        python fetch_photobook.py $start_page $end_page
        ;;
    3)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid option. Running default (all pages)..."
        python fetch_photobook.py
        ;;
esac

echo ""
echo "✅ Done! Check the output/ directory for your PDF." 