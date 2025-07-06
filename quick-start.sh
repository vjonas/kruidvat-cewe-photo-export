#!/bin/bash

# CEWE Photo Book Fetcher - Quick Start Script
# This script automates the entire deployment process

set -e

echo "🚀 CEWE Photo Book Fetcher - Quick Start"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
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

print_success() {
    echo -e "${PURPLE}$1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed!"
        echo "Please install Docker from: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed!"
        echo "Please install Docker Compose from: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    # Check OpenSSL
    if ! command -v openssl &> /dev/null; then
        print_error "OpenSSL is not installed!"
        echo "Please install OpenSSL for SSL certificate generation"
        exit 1
    fi
    
    print_status "✅ All prerequisites are installed"
}

# Interactive deployment mode selection
select_deployment_mode() {
    print_header "Select deployment mode:"
    echo "1) Development Mode (HTTP only, local access)"
    echo "2) Production Mode (HTTPS with SSL, internet access)"
    echo ""
    read -p "Enter your choice (1 or 2): " choice
    
    case $choice in
        1)
            DEPLOYMENT_MODE="dev"
            print_status "Selected: Development Mode"
            ;;
        2)
            DEPLOYMENT_MODE="prod"
            print_status "Selected: Production Mode"
            ;;
        *)
            print_error "Invalid choice. Please run the script again."
            exit 1
            ;;
    esac
}

# Setup SSL for production
setup_ssl_certificates() {
    if [ "$DEPLOYMENT_MODE" = "prod" ]; then
        print_header "Setting up SSL certificates..."
        
        # Default to the provided public IP
        PUBLIC_IP="84.197.208.166"
        
        echo ""
        print_status "Your public IP address: $PUBLIC_IP"
        read -p "Press Enter to use this IP, or type a different IP/domain: " user_input
        
        if [ ! -z "$user_input" ]; then
            PUBLIC_IP="$user_input"
        fi
        
        print_status "Generating SSL certificate for: $PUBLIC_IP"
        ./setup-ssl.sh self-signed "$PUBLIC_IP"
        
        print_warning "⚠️  Self-signed certificate will show browser security warnings"
        print_warning "⚠️  Click 'Advanced' → 'Proceed to site' in your browser"
    fi
}

# Deploy the application
deploy_application() {
    print_header "Deploying application..."
    
    if [ "$DEPLOYMENT_MODE" = "prod" ]; then
        ./deploy.sh deploy-prod
    else
        ./deploy.sh deploy
    fi
}

# Show access information
show_access_info() {
    print_header "🎉 Deployment Complete!"
    echo ""
    
    if [ "$DEPLOYMENT_MODE" = "prod" ]; then
        print_success "🌍 Your CEWE Photo Book Fetcher is now accessible from the internet!"
        echo ""
        print_status "📍 Access URLs:"
        echo "   • HTTPS: https://84.197.208.166"
        echo "   • HTTP:  http://84.197.208.166 (redirects to HTTPS)"
        echo ""
        print_warning "⚠️  Browser Security Warning:"
        echo "   • Self-signed certificate will show a warning"
        echo "   • Click 'Advanced' → 'Proceed to 84.197.208.166 (unsafe)'"
        echo "   • This is normal for self-signed certificates"
        echo ""
        print_status "🔒 Security Features:"
        echo "   • HTTPS encryption"
        echo "   • Rate limiting"
        echo "   • Security headers"
        echo "   • Container isolation"
        
    else
        print_success "🏠 Your CEWE Photo Book Fetcher is running locally!"
        echo ""
        print_status "📍 Access URLs:"
        echo "   • Local:    http://localhost:4200"
        echo "   • Network:  http://84.197.208.166:4200"
        echo ""
        print_warning "⚠️  Development mode is not secure for internet access"
        echo "   • Use production mode for internet deployment"
    fi
    
    echo ""
    print_header "📋 Management Commands:"
    echo "   • Check status:  ./deploy.sh status${DEPLOYMENT_MODE:+ prod}"
    echo "   • View logs:     ./deploy.sh logs${DEPLOYMENT_MODE:+ prod}"
    echo "   • Stop:          ./deploy.sh stop"
    echo "   • Restart:       ./deploy.sh restart${DEPLOYMENT_MODE:+ prod}"
    echo ""
    print_header "📖 Documentation:"
    echo "   • Full guide:    DOCKER_DEPLOYMENT_GUIDE.md"
    echo "   • Web interface: WEB_INTERFACE_GUIDE.md"
}

# Network setup reminder
show_network_setup() {
    if [ "$DEPLOYMENT_MODE" = "prod" ]; then
        echo ""
        print_header "🌐 Network Setup Reminder:"
        echo ""
        print_status "If you can't access from the internet, check:"
        echo "1. Router port forwarding (ports 80, 443 → your computer)"
        echo "2. Firewall settings (allow incoming on ports 80, 443)"
        echo "3. ISP restrictions (some block port 80/443)"
        echo ""
        print_status "Quick tests:"
        echo "   • Local test:    curl -I http://localhost:4200"
        echo "   • External test: curl -I https://84.197.208.166"
        echo ""
        print_status "For detailed setup help, see DOCKER_DEPLOYMENT_GUIDE.md"
    fi
}

# Main execution
main() {
    print_header "Starting automated deployment..."
    echo ""
    
    # Run setup steps
    check_prerequisites
    echo ""
    
    select_deployment_mode
    echo ""
    
    setup_ssl_certificates
    echo ""
    
    deploy_application
    echo ""
    
    show_access_info
    show_network_setup
    
    echo ""
    print_success "🚀 Setup complete! Your CEWE Photo Book Fetcher is ready to use!"
}

# Handle script interruption
trap 'echo -e "\n${RED}[ERROR]${NC} Setup interrupted. Run ./deploy.sh clean to clean up if needed."; exit 1' INT

# Run main function
main "$@" 