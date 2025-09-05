#!/bin/bash

# Whisper Service Deployment Script for Heroku

set -e

echo "🎤 Whisper v3 Service Deployment Script"
echo "========================================"

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI not found. Please install it first:"
    echo "   https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

# Check if logged in to Heroku
if ! heroku auth:whoami &> /dev/null; then
    echo "❌ Not logged in to Heroku. Please run: heroku login"
    exit 1
fi

# Get app name from user or use default
APP_NAME=${1:-"whisper-service-$(date +%s)"}

echo "📱 Creating Heroku app: $APP_NAME"

# Create Heroku app
heroku create $APP_NAME

# Set environment variables
echo "⚙️  Setting environment variables..."
heroku config:set WHISPER_MODEL_SIZE=base -a $APP_NAME

# Add buildpack for Python
echo "🔧 Adding Python buildpack..."
heroku buildpacks:add heroku/python -a $APP_NAME

# Deploy
echo "🚀 Deploying to Heroku..."
git add .
git commit -m "Deploy Whisper v3 service" || echo "No changes to commit"
git push heroku main

# Get the app URL
APP_URL=$(heroku apps:info -a $APP_NAME | grep "Web URL" | awk '{print $3}')

echo ""
echo "✅ Deployment complete!"
echo "🌐 Service URL: $APP_URL"
echo "🔍 Health check: $APP_URL/health"
echo "📚 API docs: $APP_URL/docs"
echo ""
echo "📋 Next steps:"
echo "1. Test the service: curl $APP_URL/health"
echo "2. Update your main app's REMOTE_WHISPER_URL: $APP_URL"
echo "3. Monitor logs: heroku logs --tail -a $APP_NAME"
echo ""
echo "💰 Estimated cost: ~$25/month (Standard-1X dyno)"
echo "⚡ Model: base (good balance of speed/accuracy for phone calls)"
