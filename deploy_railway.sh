#!/bin/bash

# Railway Deployment Script for Whisper v3 Service
# Cost: $5-10/month (much cheaper than Heroku!)

set -e

echo "🚂 Railway Whisper v3 Service Deployment"
echo "========================================"

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Please install it first:"
    echo "   npm install -g @railway/cli"
    echo "   or visit: https://docs.railway.app/develop/cli"
    exit 1
fi

# Check if logged in to Railway
if ! railway whoami &> /dev/null; then
    echo "❌ Not logged in to Railway. Please run: railway login"
    exit 1
fi

echo "🚀 Deploying to Railway..."

# Initialize Railway project if not exists
if [ ! -f "railway.toml" ]; then
    railway init
fi

# Set environment variables
echo "⚙️  Setting environment variables..."
railway variables set WHISPER_MODEL_SIZE=base

# Deploy
echo "🚀 Deploying to Railway..."
railway up

# Get the service URL
echo "🔍 Getting service URL..."
SERVICE_URL=$(railway domain)

echo ""
echo "✅ Deployment complete!"
echo "🌐 Service URL: $SERVICE_URL"
echo "🔍 Health check: $SERVICE_URL/health"
echo "📚 API docs: $SERVICE_URL/docs"
echo ""
echo "💰 Cost: ~$5-10/month (much cheaper than Heroku!)"
echo "⚡ Model: base (good balance of speed/accuracy)"
echo ""
echo "📋 Next steps:"
echo "1. Test the service: curl $SERVICE_URL/health"
echo "2. Update your main app's REMOTE_WHISPER_URL: $SERVICE_URL"
echo "3. Monitor logs: railway logs"
