#!/usr/bin/env python3
"""
Quick test script for the backend
"""

import sys
import os
import subprocess
import time
import requests
from pathlib import Path

def test_backend():
    """Test if backend starts and responds"""
    print("🧪 Testing backend...")
    
    project_dir = Path(__file__).parent
    backend_dir = project_dir / "backend"
    venv_dir = project_dir / "venv"
    
    # Use virtual environment Python
    if os.name == 'nt':  # Windows
        venv_python = venv_dir / "Scripts" / "python.exe"
    else:  # Unix/Linux/macOS
        venv_python = venv_dir / "bin" / "python"
    
    # Start backend server
    print("🚀 Starting backend server...")
    process = subprocess.Popen([
        str(venv_python), "app.py"
    ], cwd=backend_dir)
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(5)
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend health check passed!")
            print(f"Response: {response.json()}")
            
            # Test polling booths endpoint
            response = requests.get("http://localhost:5000/api/polling-booths", timeout=5)
            if response.status_code == 200:
                booths = response.json()
                print(f"✅ Found {len(booths)} polling booths")
                for booth in booths:
                    print(f"   - Booth {booth['booth_number']}: {booth['location']}")
            else:
                print(f"⚠️  Polling booths endpoint returned {response.status_code}")
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to connect to backend: {e}")
    
    finally:
        # Stop the server
        print("🛑 Stopping backend server...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
    
    print("✅ Backend test completed!")

if __name__ == "__main__":
    test_backend()
