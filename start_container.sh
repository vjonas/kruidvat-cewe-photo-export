#!/bin/bash

# Container-optimized CEWE Photo Book Fetcher Web Interface Starter

echo "🚀 Starting Enhanced CEWE Photo Book Fetcher Web Interface..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

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
    sys.exit(1)
"

# Create necessary directories (in case they don't exist)
mkdir -p output images temp_spreads

echo "✅ Setup complete!"
echo "🌐 Starting web interface..."
echo "📱 Access the interface at: http://localhost:4200"
echo "🔧 Press Ctrl+C to stop the server"

# Start the web interface
exec python3 web_interface.py 