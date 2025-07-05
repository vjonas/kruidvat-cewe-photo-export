#!/bin/bash

# Enhanced CEWE Photo Book Fetcher Web Interface Starter

echo "🚀 Starting Enhanced CEWE Photo Book Fetcher Web Interface..."

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

# Check if all dependencies are available
echo "🔍 Checking dependencies..."
python3 -c "
import sys
try:
    import requests, PIL, tqdm, fitz, flask, flask_socketio, bs4
    print('✅ All required dependencies are available')
except ImportError as e:
    print(f'❌ Missing dependency: {e}')
    print('⚠️  Some features may not work properly')
"

# Create necessary directories
mkdir -p output images temp_spreads

echo "✅ Setup complete!"
echo "🌐 Starting web interface..."
echo "📱 Access the interface at: http://localhost:4200"
echo "🔧 Press Ctrl+C to stop the server"

# Start the web interface
python3 web_interface.py 