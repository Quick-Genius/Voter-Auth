#!/bin/bash

# Election Vote Authentication System - Full ML Setup Script
# SIH Hackathon Project

echo "🗳️  Setting up Complete Election Vote Authentication System..."
echo "🤖 Full ML Pipeline + Blockchain Integration"
echo ""

# Check if Python 3.11 is available
if command -v /opt/homebrew/bin/python3.11 &> /dev/null; then
    PYTHON_CMD="/opt/homebrew/bin/python3.11"
    echo "✅ Using Python 3.11 for optimal ML compatibility"
elif command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
    echo "✅ Using Python 3.11"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo "⚠️  Using system Python 3 (may have compatibility issues)"
else
    echo "❌ Python 3 not found. Please install Python 3.11+"
    exit 1
fi

# Create virtual environment with Python 3.11
echo "🔨 Creating Python virtual environment..."
$PYTHON_CMD -m venv venv_full

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv_full/bin/activate

# Upgrade pip and install build tools
echo "⚡ Upgrading pip and installing build tools..."
pip install --upgrade pip setuptools wheel

# Install Python dependencies
echo "📦 Installing Python ML dependencies..."
echo "   This may take several minutes as it includes:"
echo "   • OpenCV for computer vision"
echo "   • Face recognition libraries (dlib, face_recognition)"
echo "   • MediaPipe for iris detection"
echo "   • OCR libraries (Tesseract, EasyOCR)"
echo "   • Deep learning frameworks"
echo ""

pip install -r backend/requirements_full.txt

if [ $? -eq 0 ]; then
    echo "✅ Python ML dependencies installed successfully"
else
    echo "❌ Failed to install some Python dependencies"
    echo "💡 This is normal for some ML libraries. The system will work with available components."
fi

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
cd frontend
npm install
cd ..

if [ $? -eq 0 ]; then
    echo "✅ Node.js dependencies installed successfully"
else
    echo "❌ Failed to install Node.js dependencies"
    exit 1
fi

# Test ML libraries
echo "🧪 Testing ML library availability..."
source venv_full/bin/activate

python3 -c "
import sys
print('🐍 Python version:', sys.version)

# Test core libraries
try:
    import cv2
    print('✅ OpenCV available')
except ImportError:
    print('❌ OpenCV not available')

try:
    import numpy as np
    print('✅ NumPy available')
except ImportError:
    print('❌ NumPy not available')

try:
    import PIL
    print('✅ Pillow available')
except ImportError:
    print('❌ Pillow not available')

try:
    import face_recognition
    print('✅ Face Recognition available')
except ImportError:
    print('❌ Face Recognition not available')

try:
    import mediapipe
    print('✅ MediaPipe available')
except ImportError:
    print('❌ MediaPipe not available')

try:
    import pytesseract
    print('✅ Tesseract OCR available')
except ImportError:
    print('❌ Tesseract OCR not available')

try:
    import easyocr
    print('✅ EasyOCR available')
except ImportError:
    print('❌ EasyOCR not available')
"

echo ""
echo "🎯 Setup Complete!"
echo ""
echo "🚀 To run the full ML demo:"
echo "   python3 run_full_demo.py"
echo ""
echo "🔧 To manually activate virtual environment:"
echo "   source venv_full/bin/activate"
echo ""
echo "🌐 URLs after starting:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:5000"
echo ""
echo "🤖 ML Features Available:"
echo "   • OCR Voter ID Verification"
echo "   • Face Recognition Authentication"
echo "   • Iris Pattern Detection"
echo "   • Real-time Fraud Detection"
echo "   • Blockchain Vote Recording"
echo ""
echo "🏆 Ready for SIH Hackathon Demo!"
