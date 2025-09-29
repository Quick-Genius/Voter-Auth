#!/usr/bin/env python3
"""
Full Demo Runner - Complete ML System
Election Vote Authentication System - SIH Hackathon
"""

import os
import sys
import subprocess
import time
import threading
import webbrowser
from pathlib import Path

def print_banner():
    """Print project banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        🗳️  ELECTION VOTE AUTHENTICATION SYSTEM 🗳️           ║
    ║                                                              ║
    ║                    SIH Hackathon Project                     ║
    ║                   FULL ML SYSTEM VERSION                     ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    
    🤖 Complete ML Pipeline:
    • OCR Voter ID Verification (Tesseract + EasyOCR)
    • Face Recognition (FaceNet + Dlib + DeepFace)
    • Iris Detection (OpenCV + MediaPipe)
    • Blockchain Integration (Hyperledger Fabric)
    • Real-time Fraud Detection
    • Election Commission Dashboard
    
    """
    print(banner)

def check_dependencies():
    """Check all dependencies"""
    print("🔍 Checking dependencies...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    
    # Check Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Node.js is not installed")
            return False
        print(f"✅ Node.js: {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ Node.js is not installed")
        return False
    
    print(f"✅ Python: {sys.version.split()[0]}")
    return True

def setup_backend():
    """Set up the full ML backend"""
    print("\n🔧 Setting up backend with full ML pipeline...")
    
    project_dir = Path(__file__).parent
    backend_dir = project_dir / "backend"
    venv_dir = project_dir / "venv_full"
    
    # Check if virtual environment exists
    if not venv_dir.exists():
        print("❌ Virtual environment not found. Please run setup first.")
        return False
    
    # Check if dependencies are installed
    venv_python = venv_dir / "bin" / "python" if os.name != 'nt' else venv_dir / "Scripts" / "python.exe"
    
    try:
        result = subprocess.run([
            str(venv_python), "-c", "import cv2, face_recognition, mediapipe; print('ML libraries available')"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ All ML dependencies are installed")
        else:
            print("⚠️  Some ML dependencies missing, installing...")
            subprocess.run([
                str(venv_python), "-m", "pip", "install", "-r", "backend/requirements_full.txt"
            ], cwd=project_dir, check=True)
            print("✅ ML dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install ML dependencies: {e}")
        return False
    
    return True

def setup_frontend():
    """Set up the React frontend"""
    print("\n🔧 Setting up frontend...")
    
    frontend_dir = Path(__file__).parent / "frontend"
    
    # Check if node_modules exists
    if not (frontend_dir / "node_modules").exists():
        print("📦 Installing Node.js dependencies...")
        try:
            subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
            print("✅ Frontend dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install frontend dependencies: {e}")
            return False
    else:
        print("✅ Frontend dependencies already installed")
    
    return True

def run_backend():
    """Run the full ML Flask backend"""
    print("\n🚀 Starting backend server with full ML pipeline...")
    
    project_dir = Path(__file__).parent
    venv_dir = project_dir / "venv_full"
    venv_python = venv_dir / "bin" / "python" if os.name != 'nt' else venv_dir / "Scripts" / "python.exe"
    
    try:
        process = subprocess.Popen([str(venv_python), "backend/app.py"], cwd=project_dir)
        print("✅ Backend server started on http://localhost:5000")
        return process
    except Exception as e:
        print(f"❌ Failed to start backend server: {e}")
        return None

def run_frontend():
    """Run the React frontend"""
    print("\n🚀 Starting frontend server...")
    
    frontend_dir = Path(__file__).parent / "frontend"
    
    try:
        process = subprocess.Popen(["npm", "start"], cwd=frontend_dir)
        print("✅ Frontend server started on http://localhost:3000")
        return process
    except Exception as e:
        print(f"❌ Failed to start frontend server: {e}")
        return None

def wait_for_servers():
    """Wait for servers to be ready"""
    print("\n⏳ Waiting for servers to start...")
    
    import requests
    
    # Wait for backend
    backend_ready = False
    for i in range(30):  # Wait up to 30 seconds
        try:
            response = requests.get("http://localhost:5000/api/health", timeout=2)
            if response.status_code == 200:
                backend_ready = True
                print("✅ Backend server is ready")
                break
        except:
            pass
        time.sleep(1)
    
    if not backend_ready:
        print("⚠️  Backend server may not be ready yet")
    
    # Wait for frontend
    frontend_ready = False
    for i in range(60):  # Wait up to 60 seconds for React to compile
        try:
            response = requests.get("http://localhost:3000", timeout=2)
            if response.status_code == 200:
                frontend_ready = True
                print("✅ Frontend server is ready")
                break
        except:
            pass
        time.sleep(1)
    
    if not frontend_ready:
        print("⚠️  Frontend server may not be ready yet")
    
    return backend_ready and frontend_ready

def open_browser():
    """Open the application in browser"""
    print("\n🌐 Opening application in browser...")
    time.sleep(5)  # Give servers time to start
    webbrowser.open("http://localhost:3000")

def print_demo_info():
    """Print comprehensive demo information"""
    info = """
    
    🎯 FULL ML SYSTEM DEMO READY!
    
    📱 Application URLs:
    • Frontend (User Interface): http://localhost:3000
    • Backend API: http://localhost:5000
    • Health Check: http://localhost:5000/api/health
    • Dashboard: http://localhost:3000/dashboard
    
    🤖 ML Models Active:
    • OCR Processing: Tesseract + EasyOCR for voter ID scanning
    • Face Recognition: FaceNet + Dlib + DeepFace for facial verification
    • Iris Recognition: OpenCV + MediaPipe for iris pattern analysis
    • Blockchain: Hyperledger Fabric simulation for vote recording
    
    🗳️ Complete Demo Flow:
    
    1. POLLING BOOTH SELECTION
       • 3 demo polling booths with registered voters
       • Real-time statistics and capacity monitoring
    
    2. MULTI-LAYER BIOMETRIC VERIFICATION
       • Step 1: OCR Voter ID Card Scanning (optional but recommended)
       • Step 2: Live Face Recognition with confidence scoring
       • Step 3: Advanced Iris Pattern Detection and Matching
       • Step 4: Blockchain Vote Recording
    
    3. ELECTION COMMISSION DASHBOARD
       • Real-time polling booth monitoring
       • Voter turnout analytics with charts
       • Fraud attempt detection and logging
       • Blockchain audit trail verification
    
    🔐 Sample Voter IDs for Testing:
    • Booth 001: VID001 (Rajesh Kumar), VID002 (Priya Sharma), VID003 (Amit Singh)
    • Booth 002: VID004 (Sunita Devi), VID005 (Vikram Gupta), VID006 (Meera Patel)
    • Booth 003: VID007 (Ravi Verma), VID008 (Kavita Joshi), VID009 (Deepak Yadav)
    
    🧪 Advanced Testing Scenarios:
    • Normal Voting: Complete full biometric verification flow
    • Fraud Prevention: Try voting twice with same voter ID
    • Cross-Booth Security: Try voting at incorrect polling booth
    • Biometric Quality: Test with different image qualities
    • Real-time Monitoring: Watch dashboard during voting process
    
    🎯 ML Model Features:
    • OCR: Automatic voter ID text extraction and verification
    • Face Recognition: High-accuracy facial matching with confidence scores
    • Iris Recognition: Advanced biometric security with dual-eye verification
    • Quality Assessment: Image quality scoring for all biometric inputs
    • Fraud Detection: Real-time anomaly detection and prevention
    
    🔗 Blockchain Integration:
    • Immutable vote recording on distributed ledger
    • Cryptographic hash verification for data integrity
    • Complete audit trail for transparency
    • Real-time transaction monitoring
    
    ⚡ Performance Features:
    • Sub-30 second complete verification process
    • Real-time dashboard updates
    • Concurrent voter processing capability
    • Scalable architecture for production deployment
    
    🛑 To Stop Demo:
    Press Ctrl+C in this terminal to stop all servers
    
    """
    print(info)

def cleanup_processes(processes):
    """Clean up running processes"""
    print("\n🧹 Cleaning up processes...")
    
    for process in processes:
        if process and process.poll() is None:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                try:
                    process.kill()
                except:
                    pass
    
    print("✅ Cleanup complete")

def main():
    """Main demo runner function"""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies and try again")
        return 1
    
    # Check if virtual environment exists
    venv_dir = Path(__file__).parent / "venv_full"
    if not venv_dir.exists():
        print("\n❌ Virtual environment not found!")
        print("Please run the following commands first:")
        print("  /opt/homebrew/bin/python3.11 -m venv venv_full")
        print("  source venv_full/bin/activate")
        print("  pip install -r backend/requirements_full.txt")
        return 1
    
    # Setup backend
    if not setup_backend():
        print("\n❌ Backend setup failed")
        return 1
    
    # Setup frontend
    if not setup_frontend():
        print("\n❌ Frontend setup failed")
        return 1
    
    processes = []
    
    try:
        # Start backend server
        backend_process = run_backend()
        if backend_process:
            processes.append(backend_process)
        
        # Wait for backend to start
        time.sleep(5)
        
        # Start frontend server
        frontend_process = run_frontend()
        if frontend_process:
            processes.append(frontend_process)
        
        # Wait for servers to be ready
        if wait_for_servers():
            # Open browser
            threading.Thread(target=open_browser, daemon=True).start()
        
        # Print demo information
        print_demo_info()
        
        # Keep the demo running
        print("🔄 Full ML Demo is running... Press Ctrl+C to stop")
        
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            running_processes = [p for p in processes if p and p.poll() is None]
            if len(running_processes) != len(processes):
                print("⚠️  Some processes have stopped")
                break
    
    except KeyboardInterrupt:
        print("\n\n🛑 Demo stopped by user")
    
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
    
    finally:
        cleanup_processes(processes)
    
    print("\n👋 Thank you for trying the Complete Election Vote Authentication System!")
    print("🏆 SIH Hackathon - Advanced ML + Blockchain for Democratic Security")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
