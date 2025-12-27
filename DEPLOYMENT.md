# 🚀 Deployment Guide

This guide covers multiple deployment options for making Secure Finance LLM accessible to everyone.

## Table of Contents
- [Quick Start (Local Development)](#quick-start-local-development)
- [Docker Deployment (Recommended)](#docker-deployment-recommended)
- [Cloud Deployment Options](#cloud-deployment-options)
- [Security Considerations](#security-considerations)
- [Scaling and Performance](#scaling-and-performance)

---

## Quick Start (Local Development)

### Prerequisites
- Python 3.9+ with uv
- Node.js 18+
- Docker & Docker Compose
- Ollama installed locally

### Step 1: Environment Setup
```bash
# Clone repository
git clone https://github.com/yourusername/Secure-Finance-LLM.git
cd Secure-Finance-LLM

# Copy environment template
cp .env.example .env

# Edit .env with your values (especially JWT_SECRET!)
nano .env
```

### Step 2: Start Services
```bash
# Start Qdrant vector database
cd vector_db
docker-compose up -d
cd ..

# Start Ollama and pull models
ollama pull llama3
ollama pull all-minilm

# Start backend
cd backend
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
python main.py
```

### Step 3: Start Frontend
```bash
# In a new terminal
cd frontend
npm install
npm start
```

Access at: http://localhost:3000

---

## Docker Deployment (Recommended)

The easiest way to deploy for production use.

### Full Stack Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  # Qdrant Vector Database
  qdrant:
    image: qdrant/qdrant:latest
    container_name: finance-qdrant
    ports:
      - "6333:6333"
    volumes:
      - qdrant-storage:/qdrant/storage
    restart: unless-stopped

  # Backend API
  backend:
    build:
      context: ./backend
      dockerfile: ../infra/docker/Dockerfile.backend
    container_name: finance-backend
    ports:
      - "8000:8000"
    environment:
      - QDRANT_HOST=qdrant
      - QDRANT_PORT=6333
      - LLM_BASE_URL=${LLM_BASE_URL:-http://host.docker.internal:11434}
      - JWT_SECRET=${JWT_SECRET}
    volumes:
      - ./data/pdfs:/app/data/pdfs
      - ./backend/logs:/app/logs
    depends_on:
      - qdrant
    restart: unless-stopped

  # Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: ../infra/docker/Dockerfile.frontend
    container_name: finance-frontend
    ports:
      - "3000:80"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  qdrant-storage:
```

### Deploy with Docker Compose

```bash
# Build and start all services
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop services
docker-compose -f docker-compose.prod.yml down
```

---

## Cloud Deployment Options

### Option 1: AWS Deployment

#### Using AWS ECS (Elastic Container Service)

**Architecture:**
- ECS Fargate for containerized services
- RDS for user database (optional)
- S3 for PDF storage
- Application Load Balancer for traffic distribution
- Route 53 for DNS

**Steps:**

1. **Push Docker Images to ECR:**
```bash
# Authenticate to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build and push backend
docker build -f infra/docker/Dockerfile.backend -t secure-finance-backend .
docker tag secure-finance-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/secure-finance-backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/secure-finance-backend:latest

# Build and push frontend
docker build -f infra/docker/Dockerfile.frontend -t secure-finance-frontend ./frontend
docker tag secure-finance-frontend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/secure-finance-frontend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/secure-finance-frontend:latest
```

2. **Create ECS Task Definitions** (use infra/k8s/ as reference)

3. **Set up Application Load Balancer:**
- Backend: port 8000
- Frontend: port 80
- Enable HTTPS with ACM certificate

4. **Configure Environment Variables in ECS:**
- Use AWS Secrets Manager for JWT_SECRET
- Set QDRANT_URL to managed Qdrant instance
- Configure S3 bucket for PDF storage

**Estimated Monthly Cost:** $50-150 (for small workloads)

---

### Option 2: Google Cloud Platform (GCP)

#### Using Cloud Run (Serverless)

**Steps:**

1. **Enable Required APIs:**
```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

2. **Deploy Backend:**
```bash
gcloud run deploy secure-finance-backend \
  --source ./backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars JWT_SECRET=your-secret,QDRANT_HOST=qdrant-instance
```

3. **Deploy Frontend:**
```bash
gcloud run deploy secure-finance-frontend \
  --source ./frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

4. **Set up Qdrant:**
- Use Qdrant Cloud (https://cloud.qdrant.io)
- Or deploy Qdrant on GCE VM

**Estimated Monthly Cost:** $30-100 (serverless, pay per use)

---

### Option 3: Azure Deployment

#### Using Azure Container Apps

**Steps:**

1. **Create Container Registry:**
```bash
az acr create --resource-group finance-llm-rg --name securefinancellm --sku Basic
```

2. **Build and Push Images:**
```bash
az acr build --registry securefinancellm --image backend:latest -f infra/docker/Dockerfile.backend .
az acr build --registry securefinancellm --image frontend:latest -f infra/docker/Dockerfile.frontend ./frontend
```

3. **Deploy Container Apps:**
```bash
az containerapp create \
  --name backend \
  --resource-group finance-llm-rg \
  --image securefinancellm.azurecr.io/backend:latest \
  --target-port 8000 \
  --ingress external
```

**Estimated Monthly Cost:** $40-120

---

### Option 4: DigitalOcean App Platform (Easiest)

**Perfect for quick deployment!**

1. **Connect GitHub Repository**
2. **Configure Build Settings:**
   - Backend: Python, port 8000
   - Frontend: Node, static site
3. **Set Environment Variables** in dashboard
4. **Deploy with one click!**

**Estimated Monthly Cost:** $25-75

**Pros:**
- Simplest deployment
- Automatic SSL certificates
- Built-in CI/CD
- Great for small teams

---

### Option 5: Kubernetes (For Large Scale)

Use the manifests in `infra/k8s/`:

```bash
# Create namespace
kubectl apply -f infra/k8s/namespace.yaml

# Deploy Qdrant
kubectl apply -f infra/k8s/qdrant-deployment.yaml

# Deploy backend
kubectl apply -f infra/k8s/backend-deployment.yaml

# Deploy frontend
kubectl apply -f infra/k8s/frontend-deployment.yaml

# Set up ingress for external access
kubectl apply -f infra/k8s/ingress.yaml
```

**Best for:** Enterprise deployments, auto-scaling needs

---

## Cloud Qdrant (Recommended for Production)

Instead of self-hosting Qdrant, use **Qdrant Cloud**:

1. Sign up at https://cloud.qdrant.io
2. Create a cluster (free tier available!)
3. Get your API key and cluster URL
4. Update `.env`:
```bash
QDRANT_URL=https://xyz-abc.aws.cloud.qdrant.io:6333
QDRANT_API_KEY=your-api-key-here
```

**Benefits:**
- Managed backups
- Automatic scaling
- High availability
- No maintenance

---

## Security Considerations

### 🔒 Essential Security Checklist

- [ ] **Generate Strong JWT Secret**
  ```bash
  openssl rand -hex 32
  ```

- [ ] **Enable HTTPS/TLS**
  - Use Let's Encrypt for free SSL certificates
  - Configure reverse proxy (nginx/Caddy)

- [ ] **Set Strong Admin Passwords**
  ```python
  # In backend/auth.py, replace hardcoded passwords
  # Use environment variables or database
  ```

- [ ] **Configure CORS Properly**
  ```python
  # In backend/main.py
  origins = [
      "https://yourdomain.com",  # Your production domain
      # Remove localhost in production!
  ]
  ```

- [ ] **Secure File Uploads**
  - Validate file types
  - Scan for malware
  - Limit file sizes
  - Use virus scanning service

- [ ] **Database Security**
  - Enable Qdrant authentication
  - Use private networks
  - Regular backups

- [ ] **Rate Limiting**
  ```python
  # Add to backend/main.py
  from slowapi import Limiter, _rate_limit_exceeded_handler
  from slowapi.util import get_remote_address
  
  limiter = Limiter(key_func=get_remote_address)
  app.state.limiter = limiter
  
  @app.post("/query")
  @limiter.limit("10/minute")
  async def query(...):
      ...
  ```

- [ ] **Environment Variables**
  - Never commit `.env` to git
  - Use secrets management (AWS Secrets Manager, Vault)
  - Rotate keys regularly

- [ ] **Audit Logging**
  - Already implemented in `audit_logging.py`
  - Store logs securely
  - Monitor for suspicious activity

- [ ] **Update Dependencies**
  ```bash
  # Regular security updates
  uv pip list --outdated
  npm audit fix
  ```

---

## Reverse Proxy Setup (nginx)

For production, use nginx as reverse proxy:

```nginx
# /etc/nginx/sites-available/finance-llm

server {
    listen 80;
    server_name yourdomain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    # SSL certificates (use certbot)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    
    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        client_max_body_size 50M;  # For file uploads
    }
}
```

Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/finance-llm /etc/nginx/sites-enabled/
sudo certbot --nginx -d yourdomain.com
sudo systemctl restart nginx
```

---

## Scaling and Performance

### Horizontal Scaling

**Backend:**
- Multiple backend instances behind load balancer
- Stateless design (JWT tokens)
- Shared Qdrant cluster

**Qdrant:**
- Use Qdrant Cloud with auto-scaling
- Or multi-node Qdrant cluster

**Ollama/LLM:**
- Most expensive to scale
- Consider using GPU instances (AWS p3, GCP A2)
- Or use managed LLM APIs (OpenAI, Anthropic)

### Performance Optimization

1. **Caching:**
```python
# Add Redis caching for frequent queries
from redis import Redis
cache = Redis(host='localhost', port=6379)

@app.post("/query")
async def query(request: QueryRequest):
    cache_key = f"query:{hash(request.query)}"
    cached = cache.get(cache_key)
    if cached:
        return json.loads(cached)
    # ... generate answer
    cache.setex(cache_key, 3600, json.dumps(response))
```

2. **Database Optimization:**
- Index frequently queried fields
- Use connection pooling
- Monitor query performance

3. **CDN for Frontend:**
- Use CloudFlare, Fastly, or cloud provider CDN
- Cache static assets
- Reduce latency

---

## Monitoring and Logging

### Recommended Tools

**Application Monitoring:**
- Sentry (error tracking)
- Datadog (APM)
- New Relic

**Log Aggregation:**
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Grafana + Loki
- Cloud provider solutions (CloudWatch, Stackdriver)

**Uptime Monitoring:**
- UptimeRobot (free)
- Pingdom
- StatusCake

### Health Check Endpoint

Already implemented in `backend/main.py`:
```python
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

---

## Cost Estimates

### Small Team (10-50 users)

| Component | Provider | Monthly Cost |
|-----------|----------|--------------|
| Backend Hosting | DigitalOcean App | $12 |
| Frontend Hosting | DigitalOcean App | $5 |
| Qdrant Cloud | Free Tier | $0 |
| Ollama Instance | DO Droplet 4GB | $24 |
| Domain + SSL | Namecheap/Cloudflare | $1 |
| **Total** | | **~$42/month** |

### Medium Organization (100-500 users)

| Component | Provider | Monthly Cost |
|-----------|----------|--------------|
| Backend | AWS ECS Fargate | $50 |
| Frontend | AWS S3 + CloudFront | $10 |
| Qdrant | Qdrant Cloud Standard | $50 |
| Ollama/LLM | AWS EC2 g4dn.xlarge | $150 |
| Storage | AWS S3 | $5 |
| **Total** | | **~$265/month** |

### Enterprise (1000+ users)

- Kubernetes cluster: $500+/month
- Multi-region deployment
- Dedicated GPU instances
- Custom support contracts
- **Total: $1000-5000+/month**

---

## Backup and Disaster Recovery

### Automated Backups

**Qdrant:**
```bash
# Backup script
#!/bin/bash
DATE=$(date +%Y%m%d)
docker exec finance-qdrant \
  qdrant-cli snapshot create \
  --collection-name finance_documents \
  --destination /backups/qdrant-$DATE.snapshot

# Upload to S3
aws s3 cp /backups/qdrant-$DATE.snapshot s3://your-backup-bucket/
```

**PDFs and Data:**
```bash
# Sync to cloud storage
aws s3 sync ./data/pdfs s3://your-backup-bucket/pdfs/
```

**Database (if using):**
```bash
# PostgreSQL example
pg_dump -U postgres finance_llm > backup-$DATE.sql
```

### Disaster Recovery Plan

1. **Daily automated backups**
2. **Test restore procedure monthly**
3. **Multi-region deployment for critical systems**
4. **Document recovery procedures**
5. **Monitor backup success**

---

## Next Steps

1. ✅ Choose deployment platform
2. ✅ Set up environment variables
3. ✅ Configure security settings
4. ✅ Deploy services
5. ✅ Set up monitoring
6. ✅ Configure backups
7. ✅ Test with users
8. ✅ Set up CI/CD (GitHub Actions)

---

## Support and Troubleshooting

### Common Issues

**Issue: Ollama connection failed**
- Solution: Check `LLM_BASE_URL` in .env
- For Docker: use `host.docker.internal` instead of `localhost`

**Issue: CORS errors**
- Solution: Add frontend URL to CORS origins in backend

**Issue: File upload fails**
- Solution: Check `MAX_FILE_SIZE_MB` and nginx client_max_body_size

**Issue: Slow queries**
- Solution: Increase retrieval limit, check Qdrant performance

### Getting Help

- 📧 Open GitHub Issue
- 💬 Discussion Forum (GitHub Discussions)
- 📖 Check logs in `backend/logs/`

---

## License

MIT License - See LICENSE file for details
