#!/bin/bash
# Quick start script for Gmail Summaries service

set -e

echo "🚀 Starting Gmail Summaries Service"
echo "===================================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "Please create .env file from .env.example and configure your API keys."
    echo ""
    echo "Run: cp .env.example .env"
    echo "Then edit .env with your API keys."
    exit 1
fi

# Check if credentials directory exists
if [ ! -d credentials ]; then
    echo "📁 Creating credentials directory..."
    mkdir -p credentials
    chmod 700 credentials
fi

# Check if service account file exists
if [ ! -f credentials/service-account.json ]; then
    echo "⚠️  Service account JSON file not found!"
    echo "Please copy your Google service account JSON file to:"
    echo "  credentials/service-account.json"
    exit 1
fi

# Check if docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install docker-compose first."
    exit 1
fi

echo "✅ Prerequisites check passed"
echo ""

# Build and start the service
echo "🔨 Building Docker image..."
docker-compose build

echo ""
echo "🚀 Starting service..."
docker-compose up -d

echo ""
echo "⏳ Waiting for service to be ready..."
sleep 5

# Check health
if curl -s http://localhost:5000/health > /dev/null 2>&1; then
    echo "✅ Service is running and healthy!"
    echo ""
    echo "📊 Service Status:"
    docker-compose ps
    echo ""
    echo "🔗 Health endpoint: http://localhost:5000/health"
    echo "🔗 API endpoint: http://localhost:5000/api/summarize"
    echo ""
    echo "📝 Test with:"
    echo "  curl -X POST http://localhost:5000/api/summarize \\"
    echo "    -H 'Content-Type: application/json' \\"
    echo "    -d '{\"query\": \"Summarize Today\u0027s Unread Emails\"}'"
    echo ""
    echo "📋 View logs with: docker-compose logs -f"
    echo "🛑 Stop service with: docker-compose down"
else
    echo "❌ Service failed to start properly"
    echo "Check logs with: docker-compose logs"
    exit 1
fi
