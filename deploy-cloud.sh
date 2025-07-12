#!/bin/bash

# Real Estate Wholesale Business App - Cloud Deployment Script
# Supports AWS, Google Cloud, and Azure

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
APP_NAME="real-estate-wholesale"
DOMAIN="${DOMAIN:-your-domain.com}"
CLOUD_PROVIDER="${CLOUD_PROVIDER:-aws}"
REGION="${REGION:-us-east-1}"

echo -e "${BLUE}☁️  Real Estate Wholesale Business - Cloud Deployment${NC}"
echo -e "${BLUE}===================================================${NC}"

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check cloud provider tools
check_cloud_tools() {
    case $CLOUD_PROVIDER in
        "aws")
            if ! command -v aws &> /dev/null; then
                print_error "AWS CLI is not installed. Please install it first."
                exit 1
            fi
            print_status "AWS CLI is installed"
            ;;
        "gcp")
            if ! command -v gcloud &> /dev/null; then
                print_error "Google Cloud SDK is not installed. Please install it first."
                exit 1
            fi
            print_status "Google Cloud SDK is installed"
            ;;
        "azure")
            if ! command -v az &> /dev/null; then
                print_error "Azure CLI is not installed. Please install it first."
                exit 1
            fi
            print_status "Azure CLI is installed"
            ;;
        *)
            print_error "Unsupported cloud provider: $CLOUD_PROVIDER"
            exit 1
            ;;
    esac
}

# Deploy to AWS
deploy_aws() {
    print_status "Deploying to AWS..."
    
    # Create ECS cluster
    aws ecs create-cluster --cluster-name $APP_NAME --region $REGION || true
    
    # Create ECR repositories
    aws ecr create-repository --repository-name $APP_NAME-backend --region $REGION || true
    aws ecr create-repository --repository-name $APP_NAME-frontend --region $REGION || true
    
    # Get ECR login token
    aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$REGION.amazonaws.com
    
    # Build and push images
    docker build -t $APP_NAME-backend ./real_estate_backend
    docker build -t $APP_NAME-frontend ./real_estate_frontend
    
    # Tag images
    docker tag $APP_NAME-backend:latest $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$REGION.amazonaws.com/$APP_NAME-backend:latest
    docker tag $APP_NAME-frontend:latest $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$REGION.amazonaws.com/$APP_NAME-frontend:latest
    
    # Push images
    docker push $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$REGION.amazonaws.com/$APP_NAME-backend:latest
    docker push $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$REGION.amazonaws.com/$APP_NAME-frontend:latest
    
    print_status "AWS deployment completed"
}

# Deploy to Google Cloud
deploy_gcp() {
    print_status "Deploying to Google Cloud..."
    
    # Set project
    gcloud config set project $(gcloud config get-value project)
    
    # Enable required APIs
    gcloud services enable container.googleapis.com
    gcloud services enable cloudbuild.googleapis.com
    
    # Create GKE cluster
    gcloud container clusters create $APP_NAME-cluster \
        --region $REGION \
        --num-nodes 3 \
        --machine-type e2-medium \
        --enable-autoscaling \
        --min-nodes 1 \
        --max-nodes 10 || true
    
    # Get credentials
    gcloud container clusters get-credentials $APP_NAME-cluster --region $REGION
    
    # Build and push images
    gcloud builds submit --tag gcr.io/$(gcloud config get-value project)/$APP_NAME-backend ./real_estate_backend
    gcloud builds submit --tag gcr.io/$(gcloud config get-value project)/$APP_NAME-frontend ./real_estate_frontend
    
    print_status "Google Cloud deployment completed"
}

# Deploy to Azure
deploy_azure() {
    print_status "Deploying to Azure..."
    
    # Set subscription
    az account set --subscription $(az account show --query id --output tsv)
    
    # Create resource group
    az group create --name $APP_NAME-rg --location $REGION || true
    
    # Create AKS cluster
    az aks create \
        --resource-group $APP_NAME-rg \
        --name $APP_NAME-cluster \
        --node-count 3 \
        --enable-addons monitoring \
        --generate-ssh-keys || true
    
    # Get credentials
    az aks get-credentials --resource-group $APP_NAME-rg --name $APP_NAME-cluster
    
    # Create ACR
    az acr create --resource-group $APP_NAME-rg --name $APP_NAME-acr --sku Basic || true
    
    # Build and push images
    az acr build --registry $APP_NAME-acr --image $APP_NAME-backend ./real_estate_backend
    az acr build --registry $APP_NAME-acr --image $APP_NAME-frontend ./real_estate_frontend
    
    print_status "Azure deployment completed"
}

# Create Kubernetes manifests
create_k8s_manifests() {
    print_status "Creating Kubernetes manifests..."
    
    # Create namespace
    cat > k8s/namespace.yaml << EOF
apiVersion: v1
kind: Namespace
metadata:
  name: $APP_NAME
EOF

    # Create PostgreSQL deployment
    cat > k8s/postgres.yaml << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: $APP_NAME
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15
        env:
        - name: POSTGRES_DB
          value: real_estate_db
        - name: POSTGRES_USER
          value: real_estate_user
        - name: POSTGRES_PASSWORD
          value: real_estate_password
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: $APP_NAME
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: $APP_NAME
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
EOF

    # Create backend deployment
    cat > k8s/backend.yaml << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: $APP_NAME
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: $APP_NAME-backend:latest
        env:
        - name: DATABASE_URL
          value: postgresql://real_estate_user:real_estate_password@postgres:5432/real_estate_db
        - name: SECRET_KEY
          value: $(openssl rand -hex 32)
        - name: DEBUG
          value: "False"
        ports:
        - containerPort: 8000
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: backend
  namespace: $APP_NAME
spec:
  selector:
    app: backend
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
EOF

    # Create frontend deployment
    cat > k8s/frontend.yaml << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: $APP_NAME
spec:
  replicas: 3
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: $APP_NAME-frontend:latest
        ports:
        - containerPort: 80
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: frontend
  namespace: $APP_NAME
spec:
  selector:
    app: frontend
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
EOF

    # Create ingress
    cat > k8s/ingress.yaml << EOF
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: $APP_NAME-ingress
  namespace: $APP_NAME
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - $DOMAIN
    secretName: $APP_NAME-tls
  rules:
  - host: $DOMAIN
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 80
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend
            port:
              number: 8000
EOF

    print_status "Kubernetes manifests created"
}

# Deploy to Kubernetes
deploy_k8s() {
    print_status "Deploying to Kubernetes..."
    
    # Create namespace
    kubectl apply -f k8s/namespace.yaml
    
    # Deploy PostgreSQL
    kubectl apply -f k8s/postgres.yaml
    
    # Wait for PostgreSQL to be ready
    kubectl wait --for=condition=ready pod -l app=postgres -n $APP_NAME --timeout=300s
    
    # Deploy backend
    kubectl apply -f k8s/backend.yaml
    
    # Deploy frontend
    kubectl apply -f k8s/frontend.yaml
    
    # Deploy ingress
    kubectl apply -f k8s/ingress.yaml
    
    # Wait for all pods to be ready
    kubectl wait --for=condition=ready pod -l app=backend -n $APP_NAME --timeout=300s
    kubectl wait --for=condition=ready pod -l app=frontend -n $APP_NAME --timeout=300s
    
    print_status "Kubernetes deployment completed"
}

# Show deployment information
show_cloud_info() {
    echo -e "\n${BLUE}🎉 Cloud Deployment Complete!${NC}"
    echo -e "${BLUE}============================${NC}"
    echo -e "${GREEN}Application URL:${NC} https://$DOMAIN"
    echo -e "${GREEN}API Documentation:${NC} https://$DOMAIN/docs"
    echo -e "${GREEN}Admin Login:${NC} admin / admin123"
    echo -e "\n${YELLOW}Important:${NC}"
    echo -e "• Configure your domain DNS to point to the load balancer"
    echo -e "• Set up SSL certificates (Let's Encrypt recommended)"
    echo -e "• Configure monitoring and logging"
    echo -e "• Set up database backups"
    echo -e "• Change default passwords"
    echo -e "\n${BLUE}Useful Commands:${NC}"
    echo -e "• View pods: kubectl get pods -n $APP_NAME"
    echo -e "• View logs: kubectl logs -f deployment/backend -n $APP_NAME"
    echo -e "• Scale backend: kubectl scale deployment backend --replicas=5 -n $APP_NAME"
    echo -e "• Update app: ./deploy-cloud.sh"
}

# Main deployment function
main() {
    echo -e "${BLUE}Starting cloud deployment...${NC}"
    
    # Pre-deployment checks
    check_cloud_tools
    
    # Create k8s directory
    mkdir -p k8s
    
    # Deploy based on cloud provider
    case $CLOUD_PROVIDER in
        "aws")
            deploy_aws
            ;;
        "gcp")
            deploy_gcp
            ;;
        "azure")
            deploy_azure
            ;;
    esac
    
    # Create Kubernetes manifests
    create_k8s_manifests
    
    # Deploy to Kubernetes
    deploy_k8s
    
    # Show information
    show_cloud_info
}

# Run main function
main "$@" 