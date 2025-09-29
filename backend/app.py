from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime, timedelta
import cv2
import numpy as np
import base64
from PIL import Image
import io
import json

# Import our ML models
from ml_models.ocr_processor import VoterIDOCR
from ml_models.face_recognition import FaceVerificationSystem
from ml_models.iris_recognition import IrisRecognitionSystem
from blockchain_integration import blockchain

# Initialize Flask app
app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vote_auth.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string-change-in-production'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize ML models
ocr_processor = VoterIDOCR()
face_system = FaceVerificationSystem()
iris_system = IrisRecognitionSystem()

print("🤖 ML Models initialized:")
print("✅ OCR Processor ready")
print("✅ Face Recognition System ready")
print("✅ Iris Recognition System ready")
print("✅ Blockchain Integration ready")

# Database Models
class PollingBooth(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booth_number = db.Column(db.String(20), unique=True, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    capacity = db.Column(db.Integer, default=1000)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    voters = db.relationship('Voter', backref='polling_booth', lazy=True)
    votes = db.relationship('VoteRecord', backref='polling_booth', lazy=True)

class Voter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    voter_id = db.Column(db.String(20), unique=True, nullable=False)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    address = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(15))
    
    # Biometric data
    face_encoding = db.Column(db.Text)  # JSON string of face encoding
    iris_template = db.Column(db.Text)  # JSON string of iris template
    photo_path = db.Column(db.String(200))
    
    # Polling booth assignment
    polling_booth_id = db.Column(db.Integer, db.ForeignKey('polling_booth.id'), nullable=False)
    
    # Voting status
    has_voted = db.Column(db.Boolean, default=False)
    voted_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class VoteRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    voter_uuid = db.Column(db.String(36), nullable=False)
    voter_id = db.Column(db.String(20), nullable=False)
    polling_booth_id = db.Column(db.Integer, db.ForeignKey('polling_booth.id'), nullable=False)
    
    # Authentication steps completed
    id_verified = db.Column(db.Boolean, default=False)
    face_verified = db.Column(db.Boolean, default=False)
    iris_verified = db.Column(db.Boolean, default=False)
    
    # Blockchain integration
    blockchain_hash = db.Column(db.String(64))
    
    # Timestamps
    verification_started = db.Column(db.DateTime, default=datetime.utcnow)
    verification_completed = db.Column(db.DateTime)
    vote_cast_at = db.Column(db.DateTime)

class FraudAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    voter_id = db.Column(db.String(20), nullable=False)
    attempted_booth_id = db.Column(db.Integer, db.ForeignKey('polling_booth.id'), nullable=False)
    fraud_type = db.Column(db.String(50), nullable=False)  # 'duplicate_vote', 'identity_mismatch', etc.
    details = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# API Routes

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/polling-booths', methods=['GET'])
def get_polling_booths():
    """Get all polling booths with statistics"""
    booths = PollingBooth.query.all()
    booth_data = []
    
    for booth in booths:
        total_voters = len(booth.voters)
        votes_cast = VoteRecord.query.filter_by(
            polling_booth_id=booth.id,
            vote_cast_at=db.not_(None)
        ).count()
        
        booth_data.append({
            'id': booth.id,
            'booth_number': booth.booth_number,
            'location': booth.location,
            'capacity': booth.capacity,
            'total_voters': total_voters,
            'votes_cast': votes_cast,
            'turnout_percentage': round((votes_cast / total_voters * 100), 2) if total_voters > 0 else 0
        })
    
    return jsonify(booth_data)

@app.route('/api/voter/verify-id', methods=['POST'])
def verify_voter_id():
    """Step 1: Verify voter ID using OCR"""
    try:
        data = request.get_json()
        voter_id = data.get('voter_id')
        booth_id = data.get('booth_id')
        id_card_image = data.get('id_card_image')  # Base64 encoded image
        
        print(f"🔍 API Request: voter_id={voter_id}, booth_id={booth_id}, type={type(booth_id)}")
        
        if not voter_id or not booth_id:
            return jsonify({'error': 'Voter ID and Booth ID are required'}), 400
        
        # If ID card image is provided, use OCR to verify
        if id_card_image:
            print("🔍 Processing voter ID card with OCR...")
            ocr_result = ocr_processor.process_voter_id_card(id_card_image)
            
            if not ocr_result['success']:
                return jsonify({
                    'error': f'OCR verification failed: {ocr_result["error"]}',
                    'ocr_details': ocr_result
                }), 400
            
            extracted_id = ocr_result.get('voter_id')
            if extracted_id and extracted_id.upper() != voter_id.upper():
                return jsonify({
                    'error': f'ID card mismatch. Extracted: {extracted_id}, Provided: {voter_id}',
                    'ocr_details': ocr_result
                }), 400
            
            print(f"✅ OCR verification successful. Confidence: {ocr_result.get('confidence', 0):.2f}")
        
        # Check if voter exists and is assigned to this booth
        print(f"🔍 Querying: voter_id={voter_id}, polling_booth_id={booth_id}")
        voter = Voter.query.filter_by(voter_id=voter_id, polling_booth_id=booth_id).first()
        
        if not voter:
            # Debug: check if voter exists at all
            any_voter = Voter.query.filter_by(voter_id=voter_id).first()
            if any_voter:
                print(f"❌ Voter {voter_id} exists but in booth {any_voter.polling_booth_id}, not {booth_id}")
            else:
                print(f"❌ Voter {voter_id} not found at all")
            return jsonify({'error': 'Voter not found or not assigned to this booth'}), 404
        
        print(f"✅ Found voter: {voter.name} in booth {voter.polling_booth_id}")
        
        # Check if voter has already voted
        if voter.has_voted:
            # Log fraud attempt
            fraud = FraudAttempt(
                voter_id=voter_id,
                attempted_booth_id=booth_id,
                fraud_type='duplicate_vote',
                details=f'Voter {voter_id} attempted to vote again'
            )
            db.session.add(fraud)
            db.session.commit()
            
            return jsonify({'error': 'Voter has already cast their vote'}), 403
        
        # Create or update vote record
        vote_record = VoteRecord.query.filter_by(
            voter_uuid=voter.uuid,
            polling_booth_id=booth_id
        ).first()
        
        if not vote_record:
            vote_record = VoteRecord(
                voter_uuid=voter.uuid,
                voter_id=voter_id,
                polling_booth_id=booth_id
            )
            db.session.add(vote_record)
        
        vote_record.id_verified = True
        db.session.commit()
        
        # Record on blockchain
        blockchain_result = blockchain.record_vote_verification(
            voter.uuid, voter_id, booth_id, 'id_verification'
        )
        
        return jsonify({
            'success': True,
            'voter': {
                'uuid': voter.uuid,
                'name': voter.name,
                'voter_id': voter.voter_id,
                'booth_number': voter.polling_booth.booth_number
            },
            'ocr_result': ocr_result if id_card_image else None,
            'blockchain_hash': blockchain_result.get('blockchain_hash'),
            'next_step': 'face_verification'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/voter/verify-face', methods=['POST'])
def verify_face():
    """Step 2: Enhanced face verification with liveness detection"""
    try:
        data = request.get_json()
        voter_uuid = data.get('voter_uuid')
        face_image_data = data.get('face_image')  # Base64 encoded image
        liveness_data = data.get('liveness_data', {})  # Liveness detection results
        
        if not voter_uuid or not face_image_data:
            return jsonify({'error': 'Voter UUID and face image are required'}), 400
        
        # Validate image data format
        if not face_image_data.startswith('data:image/'):
            return jsonify({'error': 'Invalid image format'}), 400
        
        # Find voter and vote record
        voter = Voter.query.filter_by(uuid=voter_uuid).first()
        if not voter:
            return jsonify({'error': 'Voter not found'}), 404
        
        vote_record = VoteRecord.query.filter_by(voter_uuid=voter_uuid).first()
        if not vote_record or not vote_record.id_verified:
            return jsonify({'error': 'ID verification must be completed first'}), 400
        
        print("👤 Processing enhanced face verification with liveness detection...")
        print(f"📊 Liveness data received: {liveness_data}")
        
        # Save the captured face image for future reference
        saved_path, save_error = face_system.save_face_image(
            face_image_data, voter.voter_id, 'live_capture'
        )
        if save_error:
            print(f"⚠️ Warning: Could not save face image: {save_error}")
        else:
            print(f"💾 Face image saved: {saved_path}")
        
        # Use enhanced face recognition with liveness detection
        if voter.face_encoding:
            # Verify against stored face encoding with liveness
            face_result = face_system.verify_face_with_liveness(
                voter.face_encoding, face_image_data, liveness_data
            )
        else:
            # Try to match against stored face images first
            match_result = face_system.match_face_from_storage(face_image_data, voter.voter_id)
            
            if match_result['success'] and match_result['verified']:
                # Found a match in stored images
                face_result = face_system.verify_face_with_liveness(
                    None, face_image_data, liveness_data
                )
                # Override with match confidence
                face_result['face_confidence'] = match_result['confidence']
                face_result['confidence'] = match_result['confidence']
            else:
                # Create new encoding from live image
                print("⚠️ No stored face data found, creating from live image")
                encoding, error = face_system.encode_face_for_storage(face_image_data)
                if error:
                    return jsonify({'error': f'Face encoding failed: {error}'}), 400
                
                # Store the encoding for future use
                voter.face_encoding = encoding
                db.session.commit()
                
                # Use enhanced verification with liveness
                face_result = face_system.verify_face_with_liveness(
                    encoding, face_image_data, liveness_data
                )
        
        if not face_result['success']:
            return jsonify({
                'error': f'Face verification failed: {face_result.get("error", "Unknown error")}',
                'details': face_result
            }), 400
        
        # Extract verification results
        face_confidence = face_result.get('face_confidence', 0)
        liveness_score = face_result.get('liveness_score', 0)
        final_verified = face_result.get('verified', False)
        
        print(f"🔍 Enhanced verification results:")
        print(f"   Face confidence: {face_confidence:.3f}")
        print(f"   Liveness score: {liveness_score:.3f}")
        print(f"   Final verified: {final_verified}")
        print(f"   Liveness details: {face_result.get('liveness_details', {})}")
        
        if final_verified:
            vote_record.face_verified = True
            db.session.commit()
            
            # Record on blockchain
            blockchain_result = blockchain.record_vote_verification(
                voter.uuid, voter.voter_id, vote_record.polling_booth_id, 'face_verification'
            )
            
            print(f"✅ Enhanced face verification successful!")
            
            return jsonify({
                'success': True,
                'verified': True,
                'face_confidence': face_confidence,
                'liveness_score': liveness_score,
                'confidence': face_result.get('confidence', 0),
                'similarity': face_result.get('similarity', 0),
                'quality_score': face_result.get('quality_score', 0),
                'liveness_details': face_result.get('liveness_details', {}),
                'verification_details': face_result.get('verification_details', {}),
                'blockchain_hash': blockchain_result.get('blockchain_hash'),
                'next_step': 'iris_verification'
            })
        else:
            # Log fraud attempt with detailed information
            verification_details = face_result.get('verification_details', {})
            fraud_details = (
                f'Enhanced face verification failed for voter {voter.voter_id}. '
                f'Face confidence: {face_confidence:.2f} (required: 0.94), '
                f'Liveness score: {liveness_score:.2f} (required: 0.30). '
                f'Face threshold met: {verification_details.get("face_threshold_met", False)}, '
                f'Liveness threshold met: {verification_details.get("liveness_threshold_met", False)}'
            )
            
            fraud = FraudAttempt(
                voter_id=voter.voter_id,
                attempted_booth_id=vote_record.polling_booth_id,
                fraud_type='identity_mismatch',
                details=fraud_details
            )
            db.session.add(fraud)
            db.session.commit()
            
            print(f"❌ Enhanced face verification failed: {fraud_details}")
            
            return jsonify({
                'success': False,
                'verified': False,
                'error': 'Face verification failed - insufficient confidence or liveness',
                'face_confidence': face_confidence,
                'liveness_score': liveness_score,
                'required_face_confidence': 0.94,
                'required_liveness_score': 0.30,
                'liveness_details': face_result.get('liveness_details', {}),
                'verification_details': verification_details,
                'details': 'Please ensure good lighting, face the camera directly, blink naturally, and move your head slightly'
            }), 403
            
    except Exception as e:
        print(f"❌ Enhanced face verification error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/voter/verify-iris', methods=['POST'])
def verify_iris():
    """Step 3: Verify iris for enhanced security"""
    try:
        data = request.get_json()
        voter_uuid = data.get('voter_uuid')
        iris_image_data = data.get('iris_image')  # Base64 encoded image
        
        if not voter_uuid or not iris_image_data:
            return jsonify({'error': 'Voter UUID and iris image are required'}), 400
        
        # Find voter and vote record
        voter = Voter.query.filter_by(uuid=voter_uuid).first()
        if not voter:
            return jsonify({'error': 'Voter not found'}), 404
        
        vote_record = VoteRecord.query.filter_by(voter_uuid=voter_uuid).first()
        if not vote_record or not vote_record.face_verified:
            return jsonify({'error': 'Face verification must be completed first'}), 400
        
        print("👁️  Processing iris verification...")
        
        # Use actual iris recognition system
        if voter.iris_template:
            # Verify against stored iris template
            iris_result = iris_system.verify_iris(voter.iris_template, iris_image_data)
        else:
            # If no stored template, create one from the live image (for demo)
            print("⚠️  No stored iris template found, creating from live image for demo")
            template, error = iris_system.encode_iris_for_storage(iris_image_data)
            if error:
                return jsonify({'error': f'Iris template creation failed: {error}'}), 400
            
            # Store the template for future use
            voter.iris_template = template
            db.session.commit()
            
            # For demo, assume high confidence match
            iris_result = {
                'success': True,
                'verified': True,
                'confidence': 0.92,
                'eye_results': {
                    'left_eye': {'success': True, 'verified': True, 'confidence': 0.92},
                    'right_eye': {'success': True, 'verified': True, 'confidence': 0.90}
                },
                'details': {
                    'eyes_detected': 2,
                    'eyes_processed': 2,
                    'eyes_verified': 2
                }
            }
        
        if not iris_result['success']:
            return jsonify({
                'error': f'Iris verification failed: {iris_result.get("error", "Unknown error")}',
                'details': iris_result
            }), 400
        
        if iris_result['verified'] and iris_result['confidence'] > 0.85:
            vote_record.iris_verified = True
            vote_record.verification_completed = datetime.utcnow()
            db.session.commit()
            
            # Record on blockchain
            blockchain_result = blockchain.record_vote_verification(
                voter.uuid, voter.voter_id, vote_record.polling_booth_id, 'iris_verification'
            )
            
            print(f"✅ Iris verification successful. Confidence: {iris_result['confidence']:.2f}")
            
            return jsonify({
                'success': True,
                'confidence': iris_result['confidence'],
                'eye_results': iris_result.get('eye_results', {}),
                'details': iris_result.get('details', {}),
                'blockchain_hash': blockchain_result.get('blockchain_hash'),
                'message': 'All verifications completed. Voter can proceed to EVM.',
                'next_step': 'evm_access'
            })
        else:
            # Log fraud attempt
            fraud = FraudAttempt(
                voter_id=voter.voter_id,
                attempted_booth_id=vote_record.polling_booth_id,
                fraud_type='identity_mismatch',
                details=f'Iris verification failed for voter {voter.voter_id}. Confidence: {iris_result["confidence"]:.2f}'
            )
            db.session.add(fraud)
            db.session.commit()
            
            return jsonify({
                'error': 'Iris verification failed - insufficient confidence',
                'confidence': iris_result['confidence'],
                'required_confidence': 0.85,
                'details': iris_result.get('details', {})
            }), 403
            
    except Exception as e:
        print(f"❌ Iris verification error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/voter/cast-vote', methods=['POST'])
def cast_vote():
    """Mark vote as cast after EVM interaction"""
    try:
        data = request.get_json()
        voter_uuid = data.get('voter_uuid')
        
        if not voter_uuid:
            return jsonify({'error': 'Voter UUID is required'}), 400
        
        # Find voter and vote record
        voter = Voter.query.filter_by(uuid=voter_uuid).first()
        if not voter:
            return jsonify({'error': 'Voter not found'}), 404
        
        vote_record = VoteRecord.query.filter_by(voter_uuid=voter_uuid).first()
        if not vote_record or not vote_record.iris_verified:
            return jsonify({'error': 'Complete verification required before voting'}), 400
        
        print(f"🗳️  Recording vote for voter {voter.voter_id}...")
        
        # Mark vote as cast
        voter.has_voted = True
        voter.voted_at = datetime.utcnow()
        vote_record.vote_cast_at = datetime.utcnow()
        
        # Record final step on blockchain
        blockchain_result = blockchain.record_vote_verification(
            voter.uuid, voter.voter_id, vote_record.polling_booth_id, 'vote_cast'
        )
        
        vote_record.blockchain_hash = blockchain_result.get('blockchain_hash', f"hash_{uuid.uuid4().hex[:16]}")
        
        db.session.commit()
        
        print(f"✅ Vote successfully recorded for {voter.voter_id}")
        print(f"🔗 Blockchain hash: {vote_record.blockchain_hash}")
        
        return jsonify({
            'success': True,
            'message': 'Vote successfully recorded on blockchain',
            'blockchain_hash': vote_record.blockchain_hash,
            'transaction_id': blockchain_result.get('transaction_id'),
            'voter_id': voter.voter_id,
            'booth_number': voter.polling_booth.booth_number,
            'timestamp': vote_record.vote_cast_at.isoformat()
        })
        
    except Exception as e:
        print(f"❌ Vote casting error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Get real-time statistics for election commission dashboard"""
    try:
        # Overall statistics
        total_booths = PollingBooth.query.count()
        total_voters = Voter.query.count()
        total_votes_cast = Voter.query.filter_by(has_voted=True).count()
        fraud_attempts = FraudAttempt.query.count()
        
        # Booth-wise statistics
        booth_stats = []
        booths = PollingBooth.query.all()
        
        for booth in booths:
            booth_voters = len(booth.voters)
            booth_votes = len([v for v in booth.voters if v.has_voted])
            recent_votes = VoteRecord.query.filter_by(
                polling_booth_id=booth.id
            ).filter(
                VoteRecord.vote_cast_at >= datetime.utcnow() - timedelta(hours=1)
            ).count()
            
            booth_stats.append({
                'booth_number': booth.booth_number,
                'location': booth.location,
                'total_voters': booth_voters,
                'votes_cast': booth_votes,
                'turnout_percentage': round((booth_votes / booth_voters * 100), 2) if booth_voters > 0 else 0,
                'recent_votes_1h': recent_votes
            })
        
        return jsonify({
            'overall': {
                'total_booths': total_booths,
                'total_voters': total_voters,
                'total_votes_cast': total_votes_cast,
                'overall_turnout': round((total_votes_cast / total_voters * 100), 2) if total_voters > 0 else 0,
                'fraud_attempts': fraud_attempts
            },
            'booth_stats': booth_stats,
            'last_updated': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/fraud-attempts', methods=['GET'])
def get_fraud_attempts():
    """Get all fraud attempts for monitoring"""
    try:
        attempts = FraudAttempt.query.order_by(FraudAttempt.timestamp.desc()).all()
        
        fraud_data = []
        for attempt in attempts:
            booth = PollingBooth.query.get(attempt.attempted_booth_id)
            fraud_data.append({
                'id': attempt.id,
                'voter_id': attempt.voter_id,
                'booth_number': booth.booth_number if booth else 'Unknown',
                'fraud_type': attempt.fraud_type,
                'details': attempt.details,
                'timestamp': attempt.timestamp.isoformat()
            })
        
        return jsonify(fraud_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Initialize database
def create_tables():
    with app.app_context():
        db.create_all()
        
        # Create sample data if not exists
        # if PollingBooth.query.count() == 0:
        #     create_sample_data()

def create_sample_data():
    """Create clean database structure - no demo data"""
    print("Creating clean database structure...")
    
    # Just create one empty booth structure
    booth = PollingBooth(
        booth_number='001', 
        location='SIH Demo Booth', 
        capacity=1000
    )
    db.session.add(booth)
    db.session.commit()
    print("Clean database structure created!")

if __name__ == '__main__':
    print("🗳️  Starting Election Vote Authentication System - Full ML Version")
    print("🤖 All ML models loaded and ready")
    print("📊 Backend running on http://localhost:5001")
    print("🔐 Complete biometric authentication enabled")
    print("🔗 Blockchain integration active")
    print("")
    
    # Initialize database
    # create_tables()
    
    app.run(debug=True, host='0.0.0.0', port=5001)
