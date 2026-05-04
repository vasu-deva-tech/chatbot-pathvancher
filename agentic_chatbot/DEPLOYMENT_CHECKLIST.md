# Deployment Checklist

Use this checklist before deploying to production.

## Pre-Deployment

- [ ] All code changes committed to git
- [ ] `.env` example updated with all required variables
- [ ] API documentation updated in README
- [ ] Error handling tested
- [ ] Logging configured correctly
- [ ] Knowledge base populated with Q&A pairs
- [ ] Security review completed

## Development Environment

- [ ] Local testing completed
- [ ] Dependencies installed without errors
- [ ] Environment variables configured
- [ ] Database/Redis connections working
- [ ] API endpoints responding correctly
- [ ] Health check endpoint working

## Docker Build

- [ ] Dockerfile syntax validated
- [ ] `.dockerignore` configured
- [ ] Build successful locally
- [ ] Image size < 200MB
  ```bash
  docker images | grep pathvancer-chatbot
  ```
- [ ] Container starts without errors
  ```bash
  docker run -e OPENAI_API_KEY=sk-... -p 8000:8000 pathvancer-chatbot:latest
  ```

## Testing

### API Testing
```bash
# Health check
curl http://localhost:8000/health

# Chat endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello",
    "session_id": "test",
    "user_id": "test@example.com"
  }'

# Session retrieval
curl http://localhost:8000/session/test

# Knowledge base
curl http://localhost:8000/knowledge-base
```

### Load Testing (optional)
```bash
# Using Apache Bench
ab -n 100 -c 10 -p data.json -T application/json http://localhost:8000/chat

# Using wrk
wrk -t4 -c100 -d30s http://localhost:8000/health
```

## Render.com Deployment

- [ ] GitHub account connected
- [ ] Repository pushed to GitHub
- [ ] Render account created
- [ ] Web Service created
- [ ] Build command verified: `pip install -r requirements.txt`
- [ ] Start command verified: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- [ ] Environment variables set:
  - [ ] `OPENAI_API_KEY`
  - [ ] `OPENAI_MODEL=gpt-3.5-turbo`
  - [ ] `DEBUG=false`
- [ ] Deployment successful
- [ ] Health check passing: `https://your-service.onrender.com/health`
- [ ] API responding to requests
- [ ] Logs monitored for errors

## AWS Elastic Beanstalk

- [ ] AWS account and permissions set up
- [ ] AWS CLI installed and configured
- [ ] `.ebextensions/python.config` in place
- [ ] EB environment initialized:
  ```bash
  eb init -p python-3.11 pathvancer-chatbot --region us-east-1
  ```
- [ ] Environment created:
  ```bash
  eb create production
  ```
- [ ] Environment variables configured:
  ```bash
  eb setenv OPENAI_API_KEY=sk-... DEBUG=false
  ```
- [ ] Deployment successful:
  ```bash
  eb deploy
  ```
- [ ] Application URL working
- [ ] Health check passing
- [ ] Logs accessible:
  ```bash
  eb logs
  ```

## AWS ECS with Docker

- [ ] ECR repository created
- [ ] AWS credentials configured
- [ ] Docker image built and tested
- [ ] Image pushed to ECR:
  ```bash
  ./deploy-ecr.sh <AWS_ACCOUNT_ID> us-east-1
  ```
- [ ] ECS cluster created
- [ ] Task definition created with:
  - [ ] Correct image URI
  - [ ] Port 8000 exposed
  - [ ] Environment variables set
  - [ ] Memory: 512MB
  - [ ] CPU: 256
- [ ] Service created with:
  - [ ] Load balancer configured
  - [ ] Auto-scaling enabled (optional)
  - [ ] Health checks configured
- [ ] Application accessible via load balancer
- [ ] CloudWatch logs configured

## Google Cloud Run

- [ ] Google Cloud account set up
- [ ] gcloud CLI installed and authenticated
- [ ] Project ID set:
  ```bash
  gcloud config set project PROJECT_ID
  ```
- [ ] Artifact Registry enabled
- [ ] Image built and pushed:
  ```bash
  gcloud builds submit --tag us-central1-docker.pkg.dev/PROJECT_ID/repo/pathvancer-chatbot
  ```
- [ ] Cloud Run service deployed:
  ```bash
  gcloud run deploy pathvancer-chatbot \
    --image us-central1-docker.pkg.dev/PROJECT_ID/repo/pathvancer-chatbot \
    --platform managed \
    --region us-central1 \
    --set-env-vars OPENAI_API_KEY=sk-...
  ```
- [ ] Service URL accessible
- [ ] Health checks passing

## Production Configuration

- [ ] `DEBUG=false` set everywhere
- [ ] HTTPS/SSL configured
- [ ] CORS settings appropriate for production domains
- [ ] Rate limiting configured (if needed)
- [ ] Monitoring/alerting set up
- [ ] Log retention configured
- [ ] Backup strategy in place

## Post-Deployment

- [ ] Application health monitored
- [ ] Error logs checked
- [ ] Performance monitored
- [ ] User-facing communication sent
- [ ] Rollback plan documented and tested
- [ ] Team notified of deployment
- [ ] Documentation updated with new deployment details

## Monitoring

- [ ] Error rate < 1%
- [ ] Response time < 1s (p95)
- [ ] CPU usage < 70%
- [ ] Memory usage < 80%
- [ ] No hanging connections
- [ ] API rate limits healthy

## Rollback Plan

If issues occur:

### Render.com
```bash
# Restart service
# (via Render dashboard)

# Redeploy previous version
git revert <commit>
git push
# Auto-deploys
```

### AWS Elastic Beanstalk
```bash
# Swap environment
eb swap production

# Or terminate and recreate
eb terminate production
eb create production
```

### AWS ECS
```bash
# Update service to previous task definition
aws ecs update-service \
  --cluster my-cluster \
  --service my-service \
  --task-definition my-task-definition:1
```

## Success Criteria

- ✅ All health checks passing
- ✅ API responding within SLA (< 500ms)
- ✅ No error rate increase
- ✅ Logs clean and informative
- ✅ Users report no issues
- ✅ Monitoring dashboards in place
- ✅ Backup/recovery tested
- ✅ Documentation complete

## Emergency Contacts

- DevOps: [contact]
- Support: [contact]
- Product: [contact]
