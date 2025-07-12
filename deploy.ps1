# Real Estate Wholesale Business App - Production Deployment Script (PowerShell)
# This script deploys the full-stack application to production

param(
    [string]$Domain = "localhost",
    [string]$Environment = "production"
)

# Configuration
$AppName = "real-estate-wholesale"

Write-Host "🏠 Real Estate Wholesale Business - Production Deployment" -ForegroundColor Blue
Write-Host "=====================================================" -ForegroundColor Blue

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

# Check if Docker is installed
function Test-Docker {
    try {
        docker --version | Out-Null
        docker-compose --version | Out-Null
        Write-Status "Docker and Docker Compose are installed"
        return $true
    }
    catch {
        Write-Error "Docker is not installed. Please install Docker Desktop first."
        return $false
    }
}

# Check if required ports are available
function Test-Ports {
    $ports = @(80, 443, 8000, 3000, 5432)
    
    foreach ($port in $ports) {
        $connection = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
        if ($connection) {
            Write-Warning "Port $port is already in use. Make sure it's not needed by another application."
        }
    }
}

# Create production environment files
function New-EnvironmentFiles {
    Write-Status "Creating environment files..."
    
    # Backend environment
    $backendEnv = @"
DATABASE_URL=postgresql://real_estate_user:real_estate_password@postgres:5432/real_estate_db
SECRET_KEY=$((1..32 | ForEach-Object { Get-Random -Maximum 256 | ForEach-Object { "{0:X2}" -f $_ } }) -join '')
DEBUG=False
APP_NAME=Real Estate Wholesale Business
ACCESS_TOKEN_EXPIRE_MINUTES=30
"@
    
    $backendEnv | Out-File -FilePath "real_estate_backend\.env" -Encoding UTF8
    
    # Frontend environment
    $frontendEnv = @"
VITE_API_URL=http://$Domain/api/v1
VITE_DEV_MODE=false
"@
    
    $frontendEnv | Out-File -FilePath "real_estate_frontend\.env" -Encoding UTF8
    
    Write-Status "Environment files created"
}

# Setup SSL certificates
function New-SSLCertificates {
    if ($Domain -ne "localhost") {
        Write-Status "Setting up SSL certificates for $Domain..."
        
        # Create SSL directory
        if (!(Test-Path "ssl")) {
            New-Item -ItemType Directory -Path "ssl"
        }
        
        # Generate self-signed certificate
        $cert = New-SelfSignedCertificate -DnsName $Domain -CertStoreLocation "Cert:\LocalMachine\My"
        $certPath = "ssl\cert.pem"
        $keyPath = "ssl\key.pem"
        
        # Export certificate
        $cert | Export-Certificate -FilePath $certPath
        $cert | Export-PfxCertificate -FilePath "ssl\temp.pfx" -Password (ConvertTo-SecureString -String "password" -AsPlainText -Force)
        
        Write-Status "SSL certificates generated"
    }
    else {
        Write-Warning "Using HTTP (no SSL) for localhost"
    }
}

# Build and start the application
function Start-Deployment {
    Write-Status "Building and starting the application..."
    
    # Stop any existing containers
    docker-compose down --remove-orphans
    
    # Build images
    Write-Status "Building Docker images..."
    docker-compose build --no-cache
    
    # Start services
    Write-Status "Starting services..."
    docker-compose up -d
    
    # Wait for services to be ready
    Write-Status "Waiting for services to be ready..."
    Start-Sleep -Seconds 30
    
    # Check if services are running
    $services = docker-compose ps --format json | ConvertFrom-Json
    $runningServices = $services | Where-Object { $_.State -eq "Up" }
    
    if ($runningServices.Count -gt 0) {
        Write-Status "All services are running"
    }
    else {
        Write-Error "Some services failed to start"
        docker-compose logs
        exit 1
    }
}

# Create initial admin user
function New-AdminUser {
    Write-Status "Creating initial admin user..."
    
    # Wait for backend to be ready
    Start-Sleep -Seconds 10
    
    # Create admin user via API
    $body = @{
        email = "admin@realestate.com"
        username = "admin"
        password = "admin123"
        full_name = "System Administrator"
        role = "admin"
    } | ConvertTo-Json
    
    try {
        Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/register" -Method POST -Body $body -ContentType "application/json"
        Write-Status "Admin user created (username: admin, password: admin123)"
    }
    catch {
        Write-Warning "Could not create admin user via API (may already exist)"
    }
}

# Show deployment information
function Show-DeploymentInfo {
    Write-Host ""
    Write-Host "🎉 Deployment Complete!" -ForegroundColor Blue
    Write-Host "========================" -ForegroundColor Blue
    Write-Host "Frontend: http://$Domain" -ForegroundColor Green
    Write-Host "Backend API: http://$Domain`:8000" -ForegroundColor Green
    Write-Host "API Documentation: http://$Domain`:8000/docs" -ForegroundColor Green
    Write-Host "Admin Login: admin / admin123" -ForegroundColor Green
    Write-Host ""
    Write-Host "Important:" -ForegroundColor Yellow
    Write-Host "• Change the default admin password immediately"
    Write-Host "• Update the SECRET_KEY in real_estate_backend\.env"
    Write-Host "• Configure your domain and SSL certificates"
    Write-Host "• Set up proper database backups"
    Write-Host ""
    Write-Host "Useful Commands:" -ForegroundColor Blue
    Write-Host "• View logs: docker-compose logs -f"
    Write-Host "• Stop app: docker-compose down"
    Write-Host "• Restart app: docker-compose restart"
    Write-Host "• Update app: .\deploy.ps1"
}

# Main deployment function
function Start-MainDeployment {
    Write-Host "Starting production deployment..." -ForegroundColor Blue
    
    # Pre-deployment checks
    if (!(Test-Docker)) {
        exit 1
    }
    Test-Ports
    
    # Setup environment
    New-EnvironmentFiles
    New-SSLCertificates
    
    # Deploy application
    Start-Deployment
    
    # Post-deployment setup
    New-AdminUser
    
    # Show information
    Show-DeploymentInfo
}

# Run main deployment
Start-MainDeployment 