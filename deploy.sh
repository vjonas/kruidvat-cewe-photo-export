#!/bin/bash

# CEWE Photo Book Fetcher Deployment Script
# This script helps deploy the web interface with Docker

set -e

echo "🚀 CEWE Photo Book Fetcher Deployment Script"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_status "Docker and Docker Compose are installed"
}

# Create necessary directories
create_directories() {
    print_header "Creating necessary directories..."
    mkdir -p output images temp_spreads
    print_status "Directories created"
}

# Build and start the application
deploy_app() {
    local mode="${1:-dev}"
    print_header "Building and starting the application in $mode mode..."
    
    # Stop any existing containers
    docker compose down 2>/dev/null || true
    docker compose -f docker-compose.prod.yml down 2>/dev/null || true
    
    # Choose compose file based on mode
    if [ "$mode" = "prod" ]; then
        if [ ! -f "ssl/cert.pem" ] || [ ! -f "ssl/key.pem" ]; then
            print_error "SSL certificates not found! Run './setup-ssl.sh self-signed' first"
            exit 1
        fi
        print_status "Using production configuration with SSL"
        docker compose -f docker-compose.prod.yml up --build -d
    else
        print_status "Using development configuration"
        docker compose up --build -d
    fi
    
    print_status "Application deployed successfully"
}

# Check application status
check_status() {
    local mode="${1:-dev}"
    print_header "Checking application status..."
    
    # Wait a bit for the container to start
    sleep 10
    
    # Choose compose file based on mode (use Docker Compose V2 syntax)
    local compose_cmd="docker compose"
    if [ "$mode" = "prod" ]; then
        compose_cmd="docker compose -f docker-compose.prod.yml"
    fi
    
    if $compose_cmd ps | grep -q "Up"; then
        print_status "✅ Application is running"
        
        if [ "$mode" = "prod" ]; then
            print_status "🔒 HTTPS access: https://84.197.208.166"
            print_status "🌍 HTTP redirect: http://84.197.208.166 (redirects to HTTPS)"
        else
            print_status "🌐 Local access: http://localhost:4200"
            print_status "🌍 External access: http://84.197.208.166:4200"
        fi
        
        # Get container logs
        echo ""
        print_header "Recent logs:"
        $compose_cmd logs --tail=20 cewe-fetcher
    else
        print_error "❌ Application failed to start"
        print_header "Error logs:"
        $compose_cmd logs cewe-fetcher
        exit 1
    fi
}

# Main deployment function
main() {
    local mode="dev"
    local command="${1:-deploy}"
    
    # Check if second argument is mode
    if [ "$2" = "prod" ] || [ "$2" = "production" ]; then
        mode="prod"
    fi
    
    case "$command" in
        "deploy")
            check_docker
            create_directories
            deploy_app "$mode"
            check_status "$mode"
            ;;
        "deploy-prod")
            mode="prod"
            check_docker
            create_directories
            deploy_app "$mode"
            check_status "$mode"
            ;;
        "start")
            print_header "Starting application..."
            if [ "$mode" = "prod" ]; then
                docker compose -f docker-compose.prod.yml up -d
            else
                docker compose up -d
            fi
            check_status "$mode"
            ;;
        "stop")
            print_header "Stopping application..."
            docker compose down 2>/dev/null || true
            docker compose -f docker-compose.prod.yml down 2>/dev/null || true
            print_status "Application stopped"
            ;;
        "restart")
            print_header "Restarting application..."
            if [ "$mode" = "prod" ]; then
                docker compose -f docker-compose.prod.yml restart
            else
                docker compose restart
            fi
            check_status "$mode"
            ;;
        "logs")
            print_header "Application logs:"
            if [ "$mode" = "prod" ]; then
                docker compose -f docker-compose.prod.yml logs -f cewe-fetcher
            else
                docker compose logs -f cewe-fetcher
            fi
            ;;
        "status")
            check_status "$mode"
            ;;
        "clean")
            print_header "Cleaning up..."
            docker compose down -v 2>/dev/null || true
            docker compose -f docker-compose.prod.yml down -v 2>/dev/null || true
            docker system prune -f
            print_status "Cleanup completed"
            ;;
        *)
            echo "Usage: $0 {deploy|deploy-prod|start|stop|restart|logs|status|clean} [prod]"
            echo ""
            echo "Commands:"
            echo "  deploy      - Deploy in development mode (http://localhost:4200)"
            echo "  deploy-prod - Deploy in production mode with SSL (https://YOUR_IP)"
            echo "  start [prod] - Start existing containers"
            echo "  stop        - Stop all containers"
            echo "  restart [prod] - Restart containers"
            echo "  logs [prod] - Show application logs"
            echo "  status [prod] - Check application status"
            echo "  clean       - Clean up all containers and images"
            echo ""
            echo "Examples:"
            echo "  $0 deploy           # Development mode"
            echo "  $0 deploy-prod      # Production mode with SSL"
            echo "  $0 start prod       # Start in production mode"
            echo ""
            echo "For production deployment:"
            echo "  1. ./setup-ssl.sh self-signed"
            echo "  2. ./deploy.sh deploy-prod"
            exit 1
            ;;
    esac
}

main "$@" 