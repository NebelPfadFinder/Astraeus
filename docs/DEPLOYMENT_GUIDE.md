Deployment Guide
Overview
This guide provides step-by-step instructions for deploying the Mistral-Qdrant Chatbot application in various environments, from local development to production deployment.
Prerequisites
System Requirements
Minimum Requirements:

CPU: 2 cores
RAM: 4GB
Storage: 10GB free space
Network: Stable internet connection

Recommended for Production:

CPU: 4+ cores
RAM: 8GB+
Storage: 50GB+ SSD
Network: High-speed connection with low latency

Software Dependencies

Docker Engine 20.10+
Docker Compose 2.0+
Git 2.30+
Python 3.9+ (for local development)

API Keys and Services

Mistral AI API Key

Sign up at https://mistral.ai
Generate an API key
Note usage limits and pricing


Qdrant Database

Can be self-hosted or use Qdrant Cloud
For production, consider Qdrant Cloud for better performance



Local Development Setup
1. Clone the Repository
bashgit clone https://github.com/your-org/mistral-qdrant-chatbot.git
cd mistral-qdrant-chatbot
2. Environment Configuration
bash# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
Required Environment Variables:
env# Mistral Configuration
MISTRAL_API_KEY=your_mistral_api_key_here
MODEL_NAME=mistral-medium
MAX_TOKENS=1000
TEMPERATURE=0.7

# Qdrant Configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333
COLLECTION_NAME=chatbot_docs
VECTOR_SIZE=1536

# Application Configuration
LOG_LEVEL=INFO
DEBUG=true
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Security
SECRET_KEY=your_secret_key_here
ALLOWED_ORIGINS=http://localhost:8501,http://127.0.0.1:8501
3. Start Development Environment
bash# Start services with Docker Compose
docker-compose -f docker-compose.dev.yml up -d

# Wait for services to be ready
docker-compose logs -f qdrant

# Initialize database
python scripts/setup_database.py

# Start the application
streamlit run app.py
4. Access the Application

Web Interface: http://localhost:8501
Qdrant Dashboard: http://localhost:6333/dashboard
Health Check: http://localhost:8501/health

Production Deployment
Option 1: Docker Compose (Recommended)
1. Prepare Production Environment
bash# Create application directory
sudo mkdir -p /opt/chatbot
cd /opt/chatbot

# Clone repository
git clone https://github.com/your-org/mistral-qdrant-chatbot.git .

# Set proper permissions
sudo chown -R $USER:$USER /opt/chatbot
2. Configure Environment
bash# Copy and edit production environment
cp .env.example .env.production
nano .env.production
Production Environment Variables:
env# Mistral Configuration
MISTRAL_API_KEY=your_production_api_key
MODEL_NAME=mistral-medium
MAX_TOKENS=1000
TEMPERATURE=0.7

# Qdrant Configuration
QDRANT_HOST=qdrant
QDRANT_PORT=6333
COLLECTION_NAME=chatbot_docs
VECTOR_SIZE=1536

# Application Configuration
LOG_LEVEL=INFO
DEBUG=false
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Security
SECRET_KEY=strong_production_secret_key
ALLOWED_ORIGINS=https://yourdomain.com
CORS_ORIGINS=https://yourdomain.com

# SSL Configuration (if using HTTPS)
SSL_CERT_PATH=/ssl/cert.pem
SSL_KEY_PATH=/ssl/key.pem

# Database Persistence
QDRANT_DATA_PATH=/data/qdrant
3. Deploy with Docker Compose
bash# Pull latest images
docker-compose pull

# Start production services
docker-compose --env-file .env.production up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
4. Initialize Production Database
bash# Run database setup
docker-compose exec app python scripts/setup_database.py

# Load initial data (optional)
docker-compose exec app python data_loader.py --path /data/initial_docs/
5. Configure Reverse Proxy (Nginx)
The included nginx.conf provides production-ready configuration:
bash# Copy nginx configuration
sudo cp nginx.conf /etc/nginx/sites-available/chatbot
sudo ln -s /etc/nginx/sites-available/chatbot /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
Option 2: Kubernetes Deployment
1. Create Namespace
bashkubectl create namespace chatbot-prod
2. Create Secrets
bash# Create secret for environment variables
kubectl create secret generic chatbot-secrets \
  --from-env-file=.env.production \
  --namespace=chatbot-prod
3. Deploy Services
yaml# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chatbot-app
  namespace: chatbot-prod
spec:
  replicas: 3
  selector:
    matchLabels:
      app: chatbot
  template:
    metadata:
      labels:
        app: chatbot
    spec:
      containers:
      - name: chatbot
        image: your-registry/chatbot:latest
        ports:
        - containerPort: 8501
        envFrom:
        - secretRef:
            name: chatbot-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
bash# Apply Kubernetes manifests
kubectl apply -f k8s/
Option 3: Cloud Platform Deployment
AWS ECS

Create ECS Cluster

bashaws ecs create-cluster --cluster-name chatbot-cluster

Build and Push Images

bash# Build image
docker build -t chatbot:latest .

# Tag for ECR
docker tag chatbot:latest your-account.dkr.ecr.region.amazonaws.com/chatbot:latest

# Push to ECR
docker push your-account.dkr.ecr.region.amazonaws.com/chatbot:latest

Create Task Definition

json{
  "family": "chatbot-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "chatbot",
      "image": "your-account.dkr.ecr.region.amazonaws.com/chatbot:latest",
      "portMappings": [
        {
          "containerPort": 8501,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "MISTRAL_API_KEY",
          "value": "your-api-key"
        }
      ]
    }
  ]
}
Google Cloud Run
bash# Build and deploy
gcloud run deploy chatbot \
  --image gcr.io/your-project/chatbot:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8501 \
  --memory 2Gi \
  --cpu 2 \
  --set-env-vars MISTRAL_API_KEY=your-api-key
SSL/TLS Configuration
Using Let's Encrypt with Certbot
bash# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal setup
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
Custom SSL Certificate
bash# Copy certificates to proper location
sudo mkdir -p /ssl
sudo cp your-cert.pem /ssl/cert.pem
sudo cp your-key.pem /ssl/key.pem
sudo chmod 600 /ssl/*
Monitoring and Logging
Health Checks
The application includes built-in health checks:
bash# Check application health
curl http://localhost:8501/health

# Check individual services
curl http://localhost:8501/health/mistral
curl http://localhost:8501/health/qdrant
Log Management
Centralized Logging with ELK Stack
yaml# docker-compose.logging.yml
version: '3.8'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.15.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"
  
  logstash:
    image: docker.elastic.co/logstash/logstash:7.15.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    ports:
      - "5000:5000"
  
  kibana:
    image: docker.elastic.co/kibana/kibana:7.15.0
    ports:
      - "5601:5601"
Log Rotation
bash# Configure logrotate
sudo nano /etc/logrotate.d/chatbot

# Content:
/var/log/chatbot/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 appuser appuser
}
Monitoring with Prometheus
yaml# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'chatbot'
    static_configs:
      - targets: ['localhost:8501']
    metrics_path: '/metrics'
Backup and Recovery
Database Backup
bash# Create backup script
#!/bin/bash
# backup_qdrant.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/qdrant"
mkdir -p $BACKUP_DIR

# Stop Qdrant temporarily
docker-compose stop qdrant

# Create backup
tar -czf $BACKUP_DIR/qdrant_backup_$DATE.tar.gz /data/qdrant/

# Restart Qdrant
docker-compose start qdrant

# Clean old backups (keep 7 days)
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
Automated Backups
bash# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /opt/chatbot/scripts/backup_qdrant.sh
Recovery Process
bash# Stop services
docker-compose down

# Restore from backup
tar -xzf /backup/qdrant/qdrant_backup_YYYYMMDD_HHMMSS.tar.gz -C /

# Start services
docker-compose up -d

# Verify recovery
python scripts/health_check.py
Scaling and Performance
Horizontal Scaling
Load Balancer Configuration
nginxupstream chatbot_backend {
    server chatbot-1:8501;
    server chatbot-2:8501;
    server chatbot-3:8501;
}

server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://chatbot_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
Auto-scaling with Docker Swarm
bash# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.prod.yml chatbot

# Scale service
docker service scale chatbot_app=5
Performance Optimization
Redis Caching
yaml# Add to docker-compose.yml
redis:
  image: redis:alpine
  ports:
    - "6379:6379"
  volumes:
    - redis_data:/data
Database Optimization
python# Optimize Qdrant configuration
{
    "vectors": {
        "size": 1536,
        "distance": "Cosine",
        "hnsw_config": {
            "m": 16,
            "ef_construct": 100
        }
    },
    "optimizers_config": {
        "deleted_threshold": 0.2,
        "vacuum_min_vector_number": 1000
    }
}
Security Hardening
Application Security

Environment Variables

Use secrets management systems
Rotate API keys regularly
Implement least privilege access


Network Security

Use private networks for internal communication
Implement firewall rules
Enable SSL/TLS everywhere


Container Security

Use non-root users
Scan images for vulnerabilities
Keep base images updated



Production Checklist

 API keys are stored securely
 SSL/TLS certificates are valid
 Firewall rules are configured
 Log monitoring is enabled
 Backup procedures are tested
 Health checks are working
 Resource limits are set
 Security updates are applied
 Documentation is updated
 Team has access credentials

Troubleshooting
Common Issues
1. Container Won't Start
bash# Check logs
docker-compose logs app

# Check resource usage
docker stats

# Verify environment variables
docker-compose config
2. Qdrant Connection Issues
bash# Test connection
curl http://localhost:6333/health

# Check Qdrant logs
docker-compose logs qdrant

# Verify network connectivity
docker-compose exec app ping qdrant
3. High Memory Usage
bash# Monitor memory usage
docker stats --no-stream

# Check for memory leaks
docker-compose exec app python scripts/memory_profiler.py

# Restart services if needed
docker-compose restart
Emergency Procedures
Service Outage

Check health endpoints
Review recent logs
Restart affected services
Scale up if needed
Contact support team

Data Loss

Stop all services immediately
Assess damage scope
Restore from latest backup
Verify data integrity
Resume operations

Maintenance
Regular Maintenance Tasks
Daily:

Monitor application logs
Check disk space usage
Verify backup completion

Weekly:

Update dependencies
Review performance metrics
Test disaster recovery

Monthly:

Security audit
Performance optimization
Documentation updates

Update Procedures
bash# Update application
git pull origin main
docker-compose build
docker-compose down
docker-compose up -d

# Verify update
python scripts/health_check.py
Support and Resources
Getting Help

Documentation: Check this guide and API docs
GitHub Issues: Report bugs and feature requests
Community: Join our Discord/Slack channel
Support Email: support@yourorganization.com

Useful Commands
bash# View all containers
docker-compose ps

# Restart specific service
docker-compose restart app

# View real-time logs
docker-compose logs -f app

# Execute command in container
docker-compose exec app bash

# Check service health
curl http://localhost:8501/health

# Monitor resource usage
docker stats
This deployment guide should help you successfully deploy the Mistral-Qdrant Chatbot in any environment. For additional assistance, please refer to the troubleshooting section or contact support.
