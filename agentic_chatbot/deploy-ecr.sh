#!/bin/bash

# Build and push Docker image to AWS ECR

set -e

AWS_ACCOUNT=$1
AWS_REGION=${2:-us-east-1}

if [ -z "$AWS_ACCOUNT" ]; then
    echo "Usage: ./deploy-ecr.sh <AWS_ACCOUNT_ID> [region]"
    exit 1
fi

echo "🚀 Building Docker image for ECR..."

# Image details
REPO_NAME="pathvancer-chatbot"
IMAGE_TAG="latest"
ECR_URL="$AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com"

# Build image
echo "Building image..."
docker build -t $REPO_NAME:$IMAGE_TAG .

# Login to ECR
echo "Logging in to ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_URL

# Create ECR repository if it doesn't exist
aws ecr describe-repositories --region $AWS_REGION --repository-names $REPO_NAME 2>/dev/null || \
aws ecr create-repository --region $AWS_REGION --repository-name $REPO_NAME

# Tag and push
echo "Tagging and pushing image..."
docker tag $REPO_NAME:$IMAGE_TAG $ECR_URL/$REPO_NAME:$IMAGE_TAG
docker push $ECR_URL/$REPO_NAME:$IMAGE_TAG

echo "✓ Image pushed to ECR!"
echo "URL: $ECR_URL/$REPO_NAME:$IMAGE_TAG"
