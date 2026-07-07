#!/bin/bash
set -e

echo "🎨 Setting up Etsy Art Agent..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install uv for faster installs (optional but recommended)
echo "⚡ Installing uv..."
pip install uv

# Install requirements
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Install agents-cli via uv (recommended)
echo "🔧 Installing agents-cli..."
uvx google-agents-cli setup

# Create local data directories
mkdir -p etsy_business_manager/data
mkdir -p eval_results

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. source venv/bin/activate"
echo "  2. export GEMINI_API_KEY='your-key'"
echo "  3. adk web"
echo "  4. Open web_interface/index.html in your browser"
