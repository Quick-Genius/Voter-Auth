# Election Vote Authentication System - SIH Hackathon

## 🗳️ Project Overview
A comprehensive voter authentication system that secures election processes through multi-layer biometric verification, preventing fraud and ensuring authentic voter identity before EVM access.

## 🎯 Problem Statement
- Voting fraud and identity verification issues
- Manual authentication lacks security
- Opposition claims of improper vote counting
- Lack of real-time polling booth data
- Need for transparent, auditable voting process

## 💡 Solution
Multi-step voter authentication system:
1. **OCR Voter ID Verification** - Automated ID card scanning and verification
2. **Face Recognition** - Biometric face matching with database
3. **Iris Detection** - Advanced biometric verification for enhanced security
4. **Blockchain Integration** - Immutable vote recording and audit trail
5. **Real-time Monitoring** - Live polling booth statistics and fraud detection

## 🛠️ Tech Stack

### Frontend
- **React.js** - Modern UI framework
- **Webcam API** - Face and iris capture
- **QR Scanner** - Voter ID scanning
- **Material-UI** - Professional UI components

### Backend
- **Python Flask** - RESTful API server
- **SQLite/PostgreSQL** - Voter database
- **JWT Authentication** - Secure session management

### Machine Learning
- **OCR**: Tesseract/EasyOCR for voter ID text extraction
- **Face Recognition**: FaceNet/Dlib for facial verification
- **Iris Recognition**: OpenCV + MediaPipe for iris detection

### Blockchain
- **Hyperledger Fabric** - Permissioned blockchain network
- **Golang Smart Contracts** - Vote recording and validation
- **Immutable Audit Trail** - Transparent vote tracking

## 🏗️ Project Structure
```
vote_auth/
├── frontend/                 # React.js application
├── backend/                  # Flask API server
├── ml_models/               # Machine learning models
├── blockchain/              # Hyperledger Fabric network
├── database/                # Database schemas and migrations
├── docs/                    # Documentation
└── demo_data/              # Sample data for 3 polling booths
```

## 🚀 Features
- ✅ Multi-layer biometric authentication
- ✅ Real-time fraud detection
- ✅ Polling booth monitoring dashboard
- ✅ Blockchain-based vote audit trail
- ✅ Cross-booth duplicate voting prevention
- ✅ Election commission admin panel
- ✅ Secure voter data management

## 🔒 Security Features
- End-to-end encryption
- Biometric data protection
- Blockchain immutability
- JWT-based authentication
- Fraud detection algorithms
- Audit trail maintenance

## 📊 Demo Scenario
- **3 Polling Booths** with registered voters
- **Sample Voter Database** with biometric data
- **Real-time Dashboard** showing booth statistics
- **Fraud Detection Demo** preventing duplicate voting

## 🎯 Hackathon Goals
- Demonstrate election security enhancement
- Showcase blockchain integration
- Prove concept feasibility
- Present scalable architecture

## 🏃‍♂️ Quick Start
```bash
# Clone and setup
git clone <repository>
cd vote_auth

# Backend setup
cd backend
pip install -r requirements.txt
python app.py

# Frontend setup
cd frontend
npm install
npm start

# Access application
http://localhost:3000
```

## 👥 Team
SIH Hackathon Team - Blockchain & Cybersecurity Domain

---
*Building secure, transparent, and fraud-proof election systems for democratic integrity.*
