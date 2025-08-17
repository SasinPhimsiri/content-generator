#!/bin/bash

# Jenosize Content Generator - Enhanced Startup Script
# Includes automated Jenosize style learning

set -e

echo "🚀 Starting Jenosize Content Generator with Style Learning..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 uv is not installed. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source ~/.bashrc
fi

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "❌ Ollama is not running. Please start Ollama first:"
    echo "   1. Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh"
    echo "   2. Start Ollama: ollama serve"
    echo "   3. Pull model: ollama pull qwen3:4b-instruct-2507-q4_K_M"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
uv sync

# Check system dependencies
echo "🔍 Checking system dependencies..."
uv run python main.py check

# Create necessary directories (simplified)
mkdir -p logs data/simple_db

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    if [ -f env.example ]; then
        cp env.example .env
        echo "✅ Created .env file from template"
    fi
fi

# Update Jenosize style learning
echo "🎯 Updating Jenosize style learning..."
uv run python main.py style

# Test content generation
echo "🧪 Testing content generation..."
uv run python main.py test

# Start the full system
echo ""
echo "🎉 Starting the complete Jenosize Content Generator..."
echo "   🌐 Frontend: http://localhost:7860"
echo "   🔗 API: http://localhost:8000"
echo "   📚 API Docs: http://localhost:8000/docs"
echo ""
echo "✨ Features enabled:"
echo "   • Multi-agent content generation"
echo "   • Automated Jenosize style learning"
echo "   • FUTURE framework integration"
echo "   • Style prompting + few-shot learning"
echo ""
echo "Press Ctrl+C to stop the system"
echo ""

uv run python main.py full
