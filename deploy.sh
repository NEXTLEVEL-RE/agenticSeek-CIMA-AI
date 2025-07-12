#!/bin/bash

# Real Estate Wholesale Business App - Production Deployment Script
# This script deploys the full-stack application to production

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="real-estate-wholesale"
DOMAIN="${DOMAIN:-localhost}"
ENVIRONMENT="${ENVIRONMENT:-production}"

echo -e "${BLUE}🏠 Real Estate Wholesale Business - Production Deployment${NC}"
echo -e "${BLUE}=====================================================${NC}"

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
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

# Check if required ports are available
check_ports() {
    local ports=("80" "443" "8000" "3000" "5432")
    
    for port in "${ports[@]}"; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
            print_warning "Port $port is already in use. Make sure it's not needed by another application."
        fi
    done
}

# Create production environment file
create_env_files() {
    print_status "Creating environment files..."
    
    # Backend environment
    cat > real_estate_backend/.env << EOF
DATABASE_URL=postgresql://real_estate_user:real_estate_password@postgres:5432/real_estate_db
SECRET_KEY=$(openssl rand -hex 32)
DEBUG=False
APP_NAME=Real Estate Wholesale Business
ACCESS_TOKEN_EXPIRE_MINUTES=30
EOF

    # Frontend environment
    cat > real_estate_frontend/.env << EOF
VITE_API_URL=http://$DOMAIN/api/v1
VITE_DEV_MODE=false
EOF

    print_status "Environment files created"
}

# Build and start the application
deploy_app() {
    print_status "Building and starting the application..."
    
    # Stop any existing containers
    docker-compose down --remove-orphans
    
    # Build images
    print_status "Building Docker images..."
    docker-compose build --no-cache
    
    # Start services
    print_status "Starting services..."
    docker-compose up -d
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 30
    
    # Check if services are running
    if docker-compose ps | grep -q "Up"; then
        print_status "All services are running"
    else
        print_error "Some services failed to start"
        docker-compose logs
        exit 1
    fi
}

# Setup SSL certificates (if domain is provided)
setup_ssl() {
    if [ "$DOMAIN" != "localhost" ]; then
        print_status "Setting up SSL certificates for $DOMAIN..."
        
        # Create SSL directory
        mkdir -p ssl
        
        # Generate self-signed certificate for testing
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout ssl/key.pem -out ssl/cert.pem \
            -subj "/C=US/ST=State/L=City/O=Organization/CN=$DOMAIN"
        
        # Update nginx config for HTTPS
        sed -i 's/# server {/server {/g' nginx.conf
        sed -i 's/#     listen 443 ssl http2;/    listen 443 ssl http2;/g' nginx.conf
        sed -i "s/#     server_name your-domain.com;/    server_name $DOMAIN;/g" nginx.conf
        sed -i 's/#     ssl_certificate/    ssl_certificate/g' nginx.conf
        sed -i 's/#     ssl_certificate_key/    ssl_certificate_key/g' nginx.conf
        sed -i 's/#     ssl_protocols/    ssl_protocols/g' nginx.conf
        sed -i 's/#     ssl_ciphers/    ssl_ciphers/g' nginx.conf
        sed -i 's/#     ssl_prefer_server_ciphers/    ssl_prefer_server_ciphers/g' nginx.conf
        sed -i 's/#     # Same location blocks as above/    # Same location blocks as above/g' nginx.conf
        sed -i 's/# }/}/g' nginx.conf
        
        print_status "SSL certificates generated"
    else
        print_warning "Using HTTP (no SSL) for localhost"
    fi
}

# Create initial admin user
create_admin_user() {
    print_status "Creating initial admin user..."
    
    # Wait for backend to be ready
    sleep 10
    
    # Create admin user via API
    curl -X POST "http://localhost:8000/api/v1/auth/register" \
        -H "Content-Type: application/json" \
        -d '{
            "email": "admin@realestate.com",
            "username": "admin",
            "password": "admin123",
            "full_name": "System Administrator",
            "role": "admin"
        }' || print_warning "Could not create admin user via API (may already exist)"
    
    print_status "Admin user created (username: admin, password: admin123)"
}

# Show deployment information
show_info() {
    echo -e "\n${BLUE}🎉 Deployment Complete!${NC}"
    echo -e "${BLUE}========================${NC}"
    echo -e "${GREEN}Frontend:${NC} http://$DOMAIN"
    echo -e "${GREEN}Backend API:${NC} http://$DOMAIN:8000"
    echo -e "${GREEN}API Documentation:${NC} http://$DOMAIN:8000/docs"
    echo -e "${GREEN}Admin Login:${NC} admin / admin123"
    echo -e "\n${YELLOW}Important:${NC}"
    echo -e "• Change the default admin password immediately"
    echo -e "• Update the SECRET_KEY in real_estate_backend/.env"
    echo -e "• Configure your domain and SSL certificates"
    echo -e "• Set up proper database backups"
    echo -e "\n${BLUE}Useful Commands:${NC}"
    echo -e "• View logs: docker-compose logs -f"
    echo -e "• Stop app: docker-compose down"
    echo -e "• Restart app: docker-compose restart"
    echo -e "• Update app: ./deploy.sh"
}

# Main deployment function
main() {
    echo -e "${BLUE}Starting production deployment...${NC}"
    
    # Pre-deployment checks
    check_docker
    check_ports
    
    # Setup environment
    create_env_files
    setup_ssl
    
    # Deploy application
    deploy_app
    
    # Post-deployment setup
    create_admin_user
    
    # Show information
    show_info
}

# Run main function
main "$@" 