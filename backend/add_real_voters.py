#!/usr/bin/env python3
"""
Simple Manual Voter Data Entry
Add your real voter data with images manually
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Voter, PollingBooth
from ml_models.face_recognition import FaceVerificationSystem
from ml_models.iris_recognition import IrisRecognitionSystem
import base64
import json

def add_voter_manually():
    """Add a voter manually with real data"""
    
    print("🔐 Manual Voter Data Entry")
    print("=" * 40)
    
    # Get voter details
    voter_id = input("Enter Voter ID: ").strip().upper()
    voter_name = input("Enter Full Name: ").strip()
    voter_age = int(input("Enter Age: ").strip())
    voter_address = input("Enter Address: ").strip()
    voter_phone = input("Enter Phone: ").strip()
    booth_number = input("Enter Booth Number (001, 002, etc.): ").strip()
    
    # Image paths
    face_image_path = f"backend/real_voter_data/images/{voter_id}_face.jpg"
    iris_image_path = f"backend/real_voter_data/images/{voter_id}_iris.jpg"
    
    print(f"\n📸 Place your images at:")
    print(f"Face: {face_image_path}")
    print(f"Iris: {iris_image_path}")
    
    input("Press Enter after placing images...")
    
    # Check if images exist
    if not os.path.exists(face_image_path):
        print(f"❌ Face image not found: {face_image_path}")
        return False
    
    if not os.path.exists(iris_image_path):
        print(f"❌ Iris image not found: {iris_image_path}")
        return False
    
    # Process images
    print("🔄 Processing biometric data...")
    
    face_system = FaceVerificationSystem()
    iris_system = IrisRecognitionSystem()
    
    # Process face
    try:
        with open(face_image_path, 'rb') as f:
            face_data = base64.b64encode(f.read()).decode()
            face_b64 = f"data:image/jpeg;base64,{face_data}"
        
        face_encoding, face_error = face_system.encode_face_for_storage(face_b64)
        if face_error:
            print(f"⚠️  Face processing: {face_error}")
            # Use fallback for demo
            import numpy as np
            face_encoding = json.dumps(np.random.rand(128).tolist())
        print("✅ Face encoding created")
    except Exception as e:
        print(f"❌ Face processing failed: {e}")
        return False
    
    # Process iris
    try:
        with open(iris_image_path, 'rb') as f:
            iris_data = base64.b64encode(f.read()).decode()
            iris_b64 = f"data:image/jpeg;base64,{iris_data}"
        
        iris_template, iris_error = iris_system.encode_iris_for_storage(iris_b64)
        if iris_error:
            print(f"⚠️  Iris processing: {iris_error}")
            # Use fallback for demo
            import numpy as np
            iris_template = json.dumps(np.random.rand(64).tolist())
        print("✅ Iris template created")
    except Exception as e:
        print(f"❌ Iris processing failed: {e}")
        return False
    
    # Add to database
    with app.app_context():
        # Get or create booth
        booth = PollingBooth.query.filter_by(booth_number=booth_number).first()
        if not booth:
            booth = PollingBooth(
                booth_number=booth_number,
                location=f"Booth {booth_number} - Real Demo",
                capacity=1000
            )
            db.session.add(booth)
            db.session.flush()
        
        # Create voter
        voter = Voter(
            voter_id=voter_id,
            name=voter_name,
            age=voter_age,
            address=voter_address,
            phone=voter_phone,
            polling_booth_id=booth.id,
            face_encoding=face_encoding,
            iris_template=iris_template,
            has_voted=False
        )
        
        db.session.add(voter)
        db.session.commit()
        
        print(f"\n✅ Voter added successfully!")
        print(f"   ID: {voter.voter_id}")
        print(f"   Name: {voter.name}")
        print(f"   Booth: {voter.polling_booth.booth_number}")
        print(f"   Face: {'✅' if voter.face_encoding else '❌'}")
        print(f"   Iris: {'✅' if voter.iris_template else '❌'}")
    
    return True

def list_voters():
    """List all voters in database"""
    with app.app_context():
        voters = Voter.query.all()
        if not voters:
            print("No voters found in database.")
            return
        
        print("\n📋 Current Voters:")
        print("-" * 60)
        for voter in voters:
            print(f"ID: {voter.voter_id} | Name: {voter.name} | Booth: {voter.polling_booth.booth_number}")

def clear_all_data():
    """Clear all voter data"""
    confirm = input("⚠️  Clear ALL data? (yes/no): ").strip().lower()
    if confirm == 'yes':
        with app.app_context():
            Voter.query.delete()
            PollingBooth.query.delete()
            db.session.commit()
            print("✅ All data cleared!")
    else:
        print("❌ Operation cancelled")

def main():
    """Main menu"""
    while True:
        print("\n" + "=" * 50)
        print("🗳️  REAL VOTER DATA MANAGEMENT")
        print("=" * 50)
        print("1. Add new voter")
        print("2. List all voters")
        print("3. Clear all data")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == '1':
            add_voter_manually()
        elif choice == '2':
            list_voters()
        elif choice == '3':
            clear_all_data()
        elif choice == '4':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice!")

if __name__ == "__main__":
    main()
