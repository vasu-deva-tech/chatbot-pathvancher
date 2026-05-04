#!/bin/bash

# Deploy to AWS Elastic Beanstalk

set -e

echo "🚀 Deploying Pathvancer Chatbot to AWS Elastic Beanstalk..."

# Check if EB is initialized
if [ ! -d ".elasticbeanstalk" ]; then
    echo "❌ EB not initialized. Run: eb init -p python-3.11 pathvancer-chatbot"
    exit 1
fi

# Set environment variables
read -p "Enter OPENAI_API_KEY: " OPENAI_API_KEY
read -p "Enter environment name [production]: " ENV_NAME
ENV_NAME=${ENV_NAME:-production}

echo "Setting environment variables..."
eb setenv OPENAI_API_KEY="$OPENAI_API_KEY" DEBUG=false

# Commit code
echo "Committing code..."
git add -A
git commit -m "Deploy: $(date +%Y-%m-%d\ %H:%M:%S)" || true

# Deploy
echo "Deploying to Elastic Beanstalk..."
eb deploy $ENV_NAME

echo "✓ Deployment complete!"
echo "View logs: eb logs"
echo "Open app: eb open"
