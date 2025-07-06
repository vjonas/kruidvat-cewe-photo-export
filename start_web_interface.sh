#!/bin/bash

# CEWE Photo Book Fetcher - Web Interface Startup Script

echo "🚀 Starting CEWE Photo Book Fetcher Web Interface..."
echo ""

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

# Create output directory if it doesn't exist
if [ ! -d "output" ]; then
    echo "📁 Creating output directory..."
    mkdir output
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 Starting web interface..."
echo "📱 Access the interface at: http://localhost:4200"
echo "🔧 Press Ctrl+C to stop the server"
echo ""

# Start the web interface
python3 web_interface.py