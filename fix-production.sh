#!/bin/bash

# Quick Fix for Werkzeug Production Error
# This script rebuilds the containers with the updated production configuration

set -e

echo "🔧 CEWE Photo Book Fetcher - Production Fix"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}$1${NC}"
}

print_header "Fixing production deployment issues..."
print_status "Addressing: Werkzeug errors, eventlet/gevent compatibility, SSL configuration"

# Stop any running containers
print_status "Stopping existing containers..."
docker compose down 2>/dev/null || true
docker compose -f docker-compose.prod.yml down 2>/dev/null || true

# Clean up containers and images
print_status "Cleaning up old containers and images..."
docker system prune -f

# Rebuild and start production deployment
print_status "Rebuilding and starting production deployment..."
if [ ! -f "ssl/cert.pem" ] || [ ! -f "ssl/key.pem" ]; then
    print_warning "SSL certificates not found. Generating self-signed certificates..."
    ./setup-ssl.sh self-signed 84.197.208.166
fi

# Start production deployment
docker compose -f docker-compose.prod.yml up --build -d

# Wait for containers to start
print_status "Waiting for containers to start..."
sleep 15

# Check status
if docker compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    print_status "✅ Production deployment is running!"
    echo ""
    print_header "Access Information:"
    echo "🔒 HTTPS: https://84.197.208.166"
    echo "🌍 HTTP:  http://84.197.208.166 (redirects to HTTPS)"
    echo ""
    print_header "Verify the fix:"
    echo "1. Check logs: ./deploy.sh logs prod"
    echo "2. Should see 'Starting in production mode with Gunicorn'"
    echo "3. No more Werkzeug errors"
    echo ""
    print_status "✅ Fix completed successfully!"
else
    print_error "❌ Production deployment failed to start"
    print_header "Debug information:"
    docker compose -f docker-compose.prod.yml logs --tail=20
    exit 1
fi 