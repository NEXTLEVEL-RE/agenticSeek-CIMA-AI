# 🚀 Production Deployment Guide

This guide covers multiple deployment options for the Real Estate Wholesale Business application.

## 📋 Prerequisites

### For All Deployments
- Docker and Docker Compose installed
- Git installed
- Domain name (optional but recommended)

### For Cloud Deployments
- Cloud provider account (AWS, Google Cloud, or Azure)
- Cloud provider CLI tools installed
- Kubernetes cluster access

## 🐳 Local Docker Deployment (Recommended for Testing)

### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd real-estate-wholesale-app

# Run the deployment script
./deploy.sh
```

### Manual Deployment
```bash
# 1. Create environment files
cp real_estate_backend/env.example real_estate_backend/.env
cp real_estate_frontend/env.example real_estate_frontend/.env

# 2. Update configuration
# Edit real_estate_backend/.env with your settings
# Edit real_estate_frontend/.env with your API URL

# 3. Build and start
docker-compose up -d

# 4. Check status
docker-compose ps
```

### Access Points
- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Admin Login**: admin / admin123

## ☁️ Cloud Deployment

### AWS Deployment

#### Prerequisites
```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS
aws configure
```

#### Deploy to AWS
```bash
# Set environment variables
export CLOUD_PROVIDER=aws
export DOMAIN=your-domain.com
export REGION=us-east-1

# Run deployment
./deploy-cloud.sh
```

### Google Cloud Deployment

#### Prerequisites
```bash
# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init
```

#### Deploy to Google Cloud
```bash
# Set environment variables
export CLOUD_PROVIDER=gcp
export DOMAIN=your-domain.com
export REGION=us-central1

# Run deployment
./deploy-cloud.sh
```

### Azure Deployment

#### Prerequisites
```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
az login
```

#### Deploy to Azure
```bash
# Set environment variables
export CLOUD_PROVIDER=azure
export DOMAIN=your-domain.com
export REGION=eastus

# Run deployment
./deploy-cloud.sh
```

## 🐧 Linux Server Deployment

### Ubuntu/Debian Server Setup

#### 1. Install Dependencies
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Nginx (optional)
sudo apt install nginx -y
```

#### 2. Deploy Application
```bash
# Clone repository
git clone <repository-url>
cd real-estate-wholesale-app

# Run deployment
./deploy.sh
```

#### 3. Configure Nginx (Optional)
```bash
# Copy nginx configuration
sudo cp nginx.conf /etc/nginx/sites-available/real-estate
sudo ln -s /etc/nginx/sites-available/real-estate /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 🔒 SSL Certificate Setup

### Let's Encrypt (Recommended)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Self-Signed Certificate (Development)
```bash
# Generate certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/key.pem -out ssl/cert.pem \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=your-domain.com"
```

## 📊 Monitoring and Logging

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Health Checks
```bash
# Check application health
curl http://localhost/health
curl http://localhost:8000/health

# Check database
docker-compose exec postgres pg_isready
```

### Performance Monitoring
```bash
# Resource usage
docker stats

# Container details
docker-compose ps
```

## 🔄 Updates and Maintenance

### Update Application
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Database Backup
```bash
# Create backup
docker-compose exec postgres pg_dump -U real_estate_user real_estate_db > backup.sql

# Restore backup
docker-compose exec -T postgres psql -U real_estate_user real_estate_db < backup.sql
```

### Scale Application
```bash
# Scale backend
docker-compose up -d --scale backend=3

# Scale frontend
docker-compose up -d --scale frontend=2
```

## 🛡️ Security Best Practices

### 1. Change Default Passwords
- Update admin password immediately after deployment
- Use strong, unique passwords
- Consider implementing password policies

### 2. Environment Variables
```bash
# Generate secure secret key
openssl rand -hex 32

# Update .env files with secure values
SECRET_KEY=your-secure-secret-key
DATABASE_PASSWORD=your-secure-db-password
```

### 3. Network Security
- Configure firewall rules
- Use HTTPS only in production
- Implement rate limiting
- Set up intrusion detection

### 4. Database Security
- Use strong database passwords
- Enable SSL connections
- Regular security updates
- Implement connection pooling

## 🔧 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using the port
sudo lsof -i :80
sudo lsof -i :8000

# Kill process or change ports
sudo kill -9 <PID>
```

#### 2. Database Connection Issues
```bash
# Check database status
docker-compose exec postgres pg_isready

# View database logs
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up -d
```

#### 3. Frontend Not Loading
```bash
# Check frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose build frontend --no-cache
docker-compose up -d frontend
```

#### 4. API Not Responding
```bash
# Check backend logs
docker-compose logs backend

# Test API directly
curl http://localhost:8000/health

# Restart backend
docker-compose restart backend
```

### Performance Issues

#### 1. High Memory Usage
```bash
# Check resource usage
docker stats

# Optimize container limits
# Add to docker-compose.yml:
# deploy:
#   resources:
#     limits:
#       memory: 512M
```

#### 2. Slow Database Queries
```bash
# Enable query logging
docker-compose exec postgres psql -U real_estate_user real_estate_db -c "SET log_statement = 'all';"

# Analyze slow queries
docker-compose exec postgres psql -U real_estate_user real_estate_db -c "SELECT * FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"
```

## 📈 Production Checklist

- [ ] Domain name configured
- [ ] SSL certificates installed
- [ ] Environment variables secured
- [ ] Database backups configured
- [ ] Monitoring and logging set up
- [ ] Firewall rules configured
- [ ] Load balancer configured (if needed)
- [ ] Auto-scaling configured (if needed)
- [ ] Disaster recovery plan in place
- [ ] Security audit completed
- [ ] Performance testing completed
- [ ] Documentation updated

## 🆘 Support

### Getting Help
1. Check the logs: `docker-compose logs`
2. Review this documentation
3. Check the API documentation: http://localhost:8000/docs
4. Create an issue in the repository

### Emergency Procedures
```bash
# Stop all services
docker-compose down

# Restart with fresh data
docker-compose down -v
docker-compose up -d

# Rollback to previous version
git checkout <previous-commit>
docker-compose down
docker-compose up -d
```

---

**Remember**: Always test deployments in a staging environment before going to production! 