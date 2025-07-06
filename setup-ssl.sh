#!/bin/bash

# SSL Certificate Setup Script for CEWE Photo Book Fetcher
# This script generates self-signed SSL certificates for HTTPS

set -e

echo "🔒 SSL Certificate Setup for CEWE Photo Book Fetcher"
echo "==================================================="

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

# Create SSL directory
create_ssl_dir() {
    print_header "Creating SSL directory..."
    mkdir -p ssl
    chmod 700 ssl
    print_status "SSL directory created"
}

# Generate self-signed certificate
generate_self_signed() {
    print_header "Generating self-signed SSL certificate..."
    
    # Get public IP or use provided IP
    PUBLIC_IP="${1:-YOUR_PUBLIC_IP}"
    
    print_status "Using IP address: $PUBLIC_IP"
    
    # Generate private key
    openssl genrsa -out ssl/key.pem 2048
    
    # Generate certificate signing request
    openssl req -new -key ssl/key.pem -out ssl/cert.csr -subj "/C=US/ST=State/L=City/O=Organization/CN=$PUBLIC_IP"
    
    # Generate self-signed certificate
    openssl x509 -req -days 365 -in ssl/cert.csr -signkey ssl/key.pem -out ssl/cert.pem
    
    # Clean up CSR
    rm ssl/cert.csr
    
    # Set proper permissions
    chmod 600 ssl/key.pem
    chmod 644 ssl/cert.pem
    
    print_status "Self-signed certificate generated successfully"
    print_warning "⚠️  This is a self-signed certificate. Browsers will show a security warning."
    print_warning "⚠️  For production use, consider using Let's Encrypt or a proper CA certificate."
}

# Setup Let's Encrypt (requires domain name)
setup_letsencrypt() {
    local domain=$1
    
    if [ -z "$domain" ]; then
        print_error "Domain name is required for Let's Encrypt"
        exit 1
    fi
    
    print_header "Setting up Let's Encrypt certificate for domain: $domain"
    
    # Check if certbot is installed
    if ! command -v certbot &> /dev/null; then
        print_status "Installing certbot..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y certbot
        elif command -v yum &> /dev/null; then
            sudo yum install -y certbot
        else
            print_error "Please install certbot manually"
            exit 1
        fi
    fi
    
    # Generate certificate
    print_status "Generating Let's Encrypt certificate..."
    sudo certbot certonly --standalone -d "$domain" --non-interactive --agree-tos --email admin@"$domain"
    
    # Copy certificates to our ssl directory
    sudo cp "/etc/letsencrypt/live/$domain/fullchain.pem" ssl/cert.pem
    sudo cp "/etc/letsencrypt/live/$domain/privkey.pem" ssl/key.pem
    sudo chown $(whoami):$(whoami) ssl/cert.pem ssl/key.pem
    chmod 644 ssl/cert.pem
    chmod 600 ssl/key.pem
    
    print_status "Let's Encrypt certificate configured successfully"
}

# Show certificate information
show_cert_info() {
    if [ -f "ssl/cert.pem" ]; then
        print_header "Certificate Information:"
        openssl x509 -in ssl/cert.pem -text -noout | grep -A 2 "Subject:"
        openssl x509 -in ssl/cert.pem -text -noout | grep -A 2 "Not After"
        print_status "Certificate files are ready in ./ssl/ directory"
    else
        print_error "No certificate found"
    fi
}

# Main function
main() {
    case "${1:-self-signed}" in
        "self-signed")
            PUBLIC_IP="${2:-84.197.208.166}"
            create_ssl_dir
            generate_self_signed "$PUBLIC_IP"
            show_cert_info
            
            echo ""
            print_header "Next Steps:"
            echo "1. Run: chmod +x deploy.sh"
            echo "2. Run: ./deploy.sh deploy"
            echo "3. Access your application at: https://$PUBLIC_IP"
            echo ""
            print_warning "Browser will show security warning for self-signed certificate"
            ;;
        "letsencrypt")
            DOMAIN="$2"
            if [ -z "$DOMAIN" ]; then
                print_error "Usage: $0 letsencrypt YOUR_DOMAIN.com"
                exit 1
            fi
            create_ssl_dir
            setup_letsencrypt "$DOMAIN"
            show_cert_info
            
            echo ""
            print_header "Next Steps:"
            echo "1. Run: chmod +x deploy.sh"
            echo "2. Run: ./deploy.sh deploy"
            echo "3. Access your application at: https://$DOMAIN"
            ;;
        "info")
            show_cert_info
            ;;
        *)
            echo "Usage: $0 {self-signed|letsencrypt|info} [IP_ADDRESS|DOMAIN]"
            echo ""
            echo "Commands:"
            echo "  self-signed [IP]    - Generate self-signed certificate (default IP: 84.197.208.166)"
            echo "  letsencrypt DOMAIN  - Setup Let's Encrypt certificate (requires domain)"
            echo "  info               - Show current certificate information"
            echo ""
            echo "Examples:"
            echo "  $0 self-signed 84.197.208.166"
            echo "  $0 letsencrypt mydomain.com"
            exit 1
            ;;
    esac
}

main "$@" 