#!/bin/bash

# Election Vote Authentication System - Setup Script
# SIH Hackathon Project

echo "🗳️  Setting up Election Vote Authentication System..."
echo ""

# Create virtual environment
echo "🔨 Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
cd frontend
npm install
cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 To run the demo:"
echo "   python3 run_demo.py"
echo ""
echo "🔧 To manually activate virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "🌐 URLs after starting:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:5000"
echo ""
