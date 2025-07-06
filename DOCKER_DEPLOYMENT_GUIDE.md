# CEWE Photo Book Fetcher - Docker Deployment Guide

This guide will help you deploy the CEWE Photo Book Fetcher web interface in a Docker container and expose it to the internet securely.

## 🏗️ Architecture Overview

The deployment consists of:
- **Flask Web Application**: Main CEWE fetcher with real-time WebSocket interface (started via `start_enhanced_web.sh`)
- **Nginx Reverse Proxy**: SSL termination, security headers, rate limiting
- **Docker Containers**: Isolated, reproducible environment with container-optimized startup
- **SSL/HTTPS**: Secure external access

## 📋 Prerequisites

### System Requirements
- Docker and Docker Compose installed
- OpenSSL (for SSL certificates)
- Ports 80 and 443 available for HTTPS access
- Sufficient disk space for photo book downloads

### Network Requirements
- Public IP address: `84.197.208.166`
- Router port forwarding configured (if behind NAT)
- Firewall rules allowing traffic on ports 80/443

## 🚀 Quick Start

### Option 1: Development Mode (HTTP only)
```bash
# Make scripts executable
chmod +x deploy.sh

# Deploy in development mode
./deploy.sh deploy

# Access: http://localhost:4200 or http://84.197.208.166:4200
```

### Option 2: Production Mode (HTTPS with SSL)
```bash
# Make scripts executable
chmod +x setup-ssl.sh deploy.sh

# Generate SSL certificates
./setup-ssl.sh self-signed 84.197.208.166

# Deploy in production mode
./deploy.sh deploy-prod

# Access: https://84.197.208.166
```

## 🔒 SSL Certificate Setup

### Self-Signed Certificates (Quick Start)
```bash
# Generate self-signed certificate for your IP
./setup-ssl.sh self-signed 84.197.208.166

# Check certificate info
./setup-ssl.sh info
```

**Note**: Browsers will show a security warning for self-signed certificates. Click "Advanced" → "Proceed to site" to continue.

### Let's Encrypt Certificates (Production)
```bash
# If you have a domain name pointing to your IP
./setup-ssl.sh letsencrypt yourdomain.com
```

## 📁 File Structure

```
oma-jeanne-photoboek/
├── cewe_fetcher.py              # Main Python script
├── web_interface.py             # Flask web application
├── start_enhanced_web.sh        # Original startup script (host system)
├── start_container.sh           # Container-optimized startup script
├── requirements.txt             # Python dependencies (includes gunicorn)
├── gunicorn.conf.py             # Gunicorn production server configuration
├── Dockerfile                   # Container definition
├── docker-compose.yml          # Development deployment
├── docker-compose.prod.yml     # Production deployment
├── nginx.conf                   # Nginx configuration
├── deploy.sh                    # Deployment script
├── setup-ssl.sh                # SSL certificate setup
├── ssl/                         # SSL certificates directory
│   ├── cert.pem                # SSL certificate
│   └── key.pem                 # Private key
├── output/                      # Generated PDFs
├── images/                      # Downloaded images
└── temp_spreads/               # Temporary files
```

## 🎛️ Deployment Commands

### Main Commands
```bash
# Full deployment commands
./deploy.sh deploy              # Development mode (HTTP)
./deploy.sh deploy-prod         # Production mode (HTTPS)

# Container management
./deploy.sh start [prod]        # Start containers
./deploy.sh stop                # Stop all containers
./deploy.sh restart [prod]      # Restart containers
./deploy.sh status [prod]       # Check status
./deploy.sh logs [prod]         # View logs
./deploy.sh clean               # Clean up everything
```

### Examples
```bash
# Development deployment
./deploy.sh deploy

# Production deployment with SSL
./setup-ssl.sh self-signed 84.197.208.166
./deploy.sh deploy-prod

# Check production status
./deploy.sh status prod

# View production logs
./deploy.sh logs prod
```

## 🌐 Network Configuration

### Router Port Forwarding
Configure your router to forward external traffic to your computer:

1. **Access Router Admin Panel**
   - Usually `192.168.1.1` or `192.168.0.1`
   - Login with admin credentials

2. **Port Forwarding Rules**
   ```
   Service: HTTP
   External Port: 80
   Internal IP: YOUR_LOCAL_IP
   Internal Port: 80
   Protocol: TCP
   
   Service: HTTPS  
   External Port: 443
   Internal IP: YOUR_LOCAL_IP
   Internal Port: 443
   Protocol: TCP
   ```

3. **Find Your Local IP**
   ```bash
   # On macOS/Linux
   ifconfig | grep "inet " | grep -v 127.0.0.1
   
   # On Windows
   ipconfig | findstr "IPv4"
   ```

### Firewall Configuration

#### macOS
```bash
# Allow incoming connections
sudo pfctl -e
sudo pfctl -f /etc/pf.conf
```

#### Linux (Ubuntu/Debian)
```bash
# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

#### Windows
```bash
# Open Windows Defender Firewall
# Add inbound rules for ports 80 and 443
```

## 🚀 Startup Scripts

The project includes two startup scripts for different environments:

### Host System Startup
```bash
# For running directly on your computer (non-Docker)
./start_enhanced_web.sh
```
This script:
- Creates a Python virtual environment
- Installs dependencies from requirements.txt
- Performs dependency checks
- Creates necessary directories
- Starts the web interface

### Container Startup
```bash
# Used automatically inside Docker containers
./start_container.sh
```
This container-optimized script:
- Skips virtual environment creation (container provides isolation)
- Assumes dependencies are pre-installed (during Docker build)
- Performs dependency validation
- Creates necessary directories
- Starts the web interface

The Docker setup automatically uses the container-optimized script while maintaining compatibility with the original startup process.

### Production vs Development Servers

The application automatically chooses the appropriate server based on the environment:

**Development Mode** (`FLASK_ENV != production`):
- Uses Flask's built-in Werkzeug server
- Allows unsafe Werkzeug for development convenience
- Suitable for local testing and development

**Production Mode** (`FLASK_ENV=production`):
- Uses Gunicorn WSGI server with eventlet workers
- Supports WebSocket connections via Flask-SocketIO
- Optimized for production workloads
- Automatic worker management and restart
- Better performance and security

## 🔧 Configuration Options

### Environment Variables
Create a `.env` file for custom configuration:
```env
# Flask configuration
FLASK_ENV=production
SECRET_KEY=your-secret-key-here

# Application settings
DEFAULT_WIDTH=1080
MAX_CONCURRENT_JOBS=3
TIMEOUT_SECONDS=300
```

### Volume Mounts
Data persistence is configured in `docker-compose.yml`:
```yaml
volumes:
  - ./output:/app/output          # PDF outputs
  - ./images:/app/images          # Downloaded images  
  - ./temp_spreads:/app/temp_spreads  # Temporary files
```

## 📊 Monitoring and Troubleshooting

### Health Checks
```bash
# Check container health
docker ps

# Check application logs
./deploy.sh logs [prod]

# Test connectivity
curl -I http://localhost:4200     # Development
curl -I https://84.197.208.166    # Production
```

### Common Issues

#### SSL Certificate Errors
```bash
# Regenerate certificates
./setup-ssl.sh self-signed 84.197.208.166

# Check certificate validity
openssl x509 -in ssl/cert.pem -text -noout
```

#### Container Won't Start
```bash
# Check logs for errors
./deploy.sh logs

# Clean and rebuild
./deploy.sh clean
./deploy.sh deploy
```

#### Cannot Access from Internet
1. Verify public IP: `curl ifconfig.me`
2. Check port forwarding in router
3. Verify firewall rules
4. Test local access first

#### Werkzeug Production Error
If you see "RuntimeError: The Werkzeug web server is not designed to run in production":

```bash
# Check if FLASK_ENV is set to production
./deploy.sh logs prod

# If the error persists, rebuild the container
./deploy.sh clean
./deploy.sh deploy-prod

# Verify gunicorn is installed
docker-compose -f docker-compose.prod.yml exec cewe-fetcher pip list | grep gunicorn
```

**Cause**: The application tries to use Flask's development server in production mode.
**Solution**: The container now automatically uses Gunicorn in production mode (FLASK_ENV=production).

## 🔐 Security Considerations

### Production Security Features
- **HTTPS Only**: All HTTP traffic redirects to HTTPS
- **Security Headers**: XSS protection, content type sniffing prevention
- **Rate Limiting**: API endpoint protection
- **Container Isolation**: Non-root user execution
- **Network Segmentation**: Internal Docker network

### Additional Security Measures
```bash
# Change default secrets
# Edit docker-compose.prod.yml and update:
environment:
  - SECRET_KEY=your-unique-secret-key

# Regular updates
docker system prune -f
./deploy.sh clean
./deploy.sh deploy-prod
```

## 📈 Performance Optimization

### System Resources
```bash
# Monitor resource usage
docker stats

# Limit container resources (add to docker-compose.yml)
deploy:
  resources:
    limits:
      memory: 2g
      cpus: '1.0'
```

### Nginx Caching
Add to `nginx.conf` for static file caching:
```nginx
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## 🆘 Support and Maintenance

### Log Locations
```bash
# Application logs
./deploy.sh logs

# Nginx logs (production)
docker-compose -f docker-compose.prod.yml logs nginx

# System logs
journalctl -u docker
```

### Backup Important Data
```bash
# Backup output directory
tar -czf backup-$(date +%Y%m%d).tar.gz output/

# Backup SSL certificates
tar -czf ssl-backup-$(date +%Y%m%d).tar.gz ssl/
```

### Updates and Maintenance
```bash
# Update containers
./deploy.sh stop
git pull  # If using version control
./deploy.sh deploy-prod

# Clean up old images
docker system prune -a
```

## 📞 Access Information

After successful deployment:

### Development Mode
- **Local Access**: http://localhost:4200
- **External Access**: http://84.197.208.166:4200

### Production Mode  
- **HTTPS Access**: https://84.197.208.166
- **HTTP Redirect**: http://84.197.208.166 → https://84.197.208.166

## 🎯 Next Steps

1. **Test the deployment** with a sample CEWE URL
2. **Configure monitoring** with uptime checks
3. **Set up backups** for important data
4. **Consider a domain name** for easier access
5. **Monitor logs** for any issues

Your CEWE Photo Book Fetcher is now ready for internet access! 🚀 