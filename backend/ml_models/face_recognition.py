import cv2
import numpy as np
import base64
import io
from PIL import Image
import json
import pickle

# Try to import face recognition libraries with fallbacks
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    print("⚠️  face_recognition library not available, using OpenCV fallback")

try:
    import dlib
    DLIB_AVAILABLE = True
except ImportError:
    DLIB_AVAILABLE = False
    print("⚠️  dlib library not available, using OpenCV fallback")

try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except ImportError:
    DEEPFACE_AVAILABLE = False
    print("⚠️  DeepFace library not available, using basic face detection")

class FaceVerificationSystem:
    """Advanced face recognition system for voter authentication"""
    
    def __init__(self):
        # Initialize face detector based on available libraries
        if DLIB_AVAILABLE:
            self.face_detector = dlib.get_frontal_face_detector()
            self.shape_predictor = None
        else:
            # Use OpenCV's Haar cascade as fallback
            self.face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.shape_predictor = None
        
        # Face recognition models
        self.models = ['VGG-Face', 'Facenet', 'OpenFace', 'DeepFace']
        self.default_model = 'Facenet'
        
        # Verification thresholds
        self.verification_threshold = 0.6
        self.confidence_threshold = 0.8
        
        # Check available libraries
        self.face_recognition_available = FACE_RECOGNITION_AVAILABLE
        self.dlib_available = DLIB_AVAILABLE
        self.deepface_available = DEEPFACE_AVAILABLE
        
    def preprocess_image(self, image_data):
        """Preprocess image for face recognition"""
        try:
            # Handle base64 encoded images
            if isinstance(image_data, str):
                if 'data:image' in image_data:
                    image_data = image_data.split(',')[1]
                
                image_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(image_bytes))
                image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            else:
                image = image_data
            
            # Resize image if too large
            height, width = image.shape[:2]
            if width > 800:
                scale = 800 / width
                new_width = int(width * scale)
                new_height = int(height * scale)
                image = cv2.resize(image, (new_width, new_height))
            
            return image
            
        except Exception as e:
            print(f"Error preprocessing image: {str(e)}")
            return None
    
    def detect_faces(self, image):
        """Detect faces in the image"""
        try:
            if self.face_recognition_available:
                # Use face_recognition library (preferred)
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                face_locations = face_recognition.face_locations(rgb_image)
                
                if not face_locations:
                    return None, "No face detected in the image"
                
                if len(face_locations) > 1:
                    return None, "Multiple faces detected. Please ensure only one face is visible"
                
                return face_locations[0], None
            
            else:
                # Use OpenCV Haar cascade fallback
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                faces = self.face_detector.detectMultiScale(gray, 1.1, 4)
                
                if len(faces) == 0:
                    return None, "No face detected in the image"
                
                if len(faces) > 1:
                    return None, "Multiple faces detected. Please ensure only one face is visible"
                
                # Convert OpenCV format (x, y, w, h) to face_recognition format (top, right, bottom, left)
                x, y, w, h = faces[0]
                face_location = (y, x + w, y + h, x)
                return face_location, None
            
        except Exception as e:
            return None, f"Face detection failed: {str(e)}"
    
    def extract_face_encoding(self, image, face_location=None):
        """Extract face encoding using available libraries"""
        try:
            if self.face_recognition_available:
                # Use face_recognition library (preferred)
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                
                if face_location:
                    face_encodings = face_recognition.face_encodings(rgb_image, [face_location])
                else:
                    face_encodings = face_recognition.face_encodings(rgb_image)
                
                if not face_encodings:
                    return None, "Could not generate face encoding"
                
                return face_encodings[0], None
            
            else:
                # Fallback: Create a simple feature vector from face region
                if face_location:
                    top, right, bottom, left = face_location
                    face_image = image[top:bottom, left:right]
                else:
                    face_image = image
                
                # Resize to standard size
                face_image = cv2.resize(face_image, (128, 128))
                
                # Convert to grayscale and flatten as a simple feature vector
                gray_face = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
                
                # Apply some basic feature extraction (histogram)
                hist = cv2.calcHist([gray_face], [0], None, [256], [0, 256])
                
                # Normalize and create a simple encoding
                encoding = hist.flatten() / np.sum(hist)
                
                return encoding, None
            
        except Exception as e:
            return None, f"Face encoding failed: {str(e)}"
    
    def extract_deepface_embedding(self, image):
        """Extract face embedding using DeepFace"""
        try:
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Extract embedding
            embedding = DeepFace.represent(
                img_path=rgb_image,
                model_name=self.default_model,
                enforce_detection=True
            )
            
            return embedding[0]['embedding'], None
            
        except Exception as e:
            return None, f"DeepFace embedding failed: {str(e)}"
    
    def compare_faces_basic(self, known_encoding, unknown_encoding):
        """Basic face comparison using available methods"""
        try:
            if self.face_recognition_available:
                # Use face_recognition library (preferred)
                distance = face_recognition.face_distance([known_encoding], unknown_encoding)[0]
                similarity = 1 - distance
                is_match = distance < self.verification_threshold
            else:
                # Fallback: Use cosine similarity for histogram comparison
                # Normalize encodings
                known_norm = known_encoding / (np.linalg.norm(known_encoding) + 1e-8)
                unknown_norm = unknown_encoding / (np.linalg.norm(unknown_encoding) + 1e-8)
                
                # Calculate cosine similarity
                similarity = np.dot(known_norm, unknown_norm)
                distance = 1 - similarity
                is_match = similarity > (1 - self.verification_threshold)  # Invert for similarity
            
            return {
                'is_match': is_match,
                'similarity': float(similarity),
                'distance': float(distance),
                'confidence': float(similarity) if is_match else 0.0
            }
            
        except Exception as e:
            return {
                'is_match': False,
                'similarity': 0.0,
                'distance': 1.0,
                'confidence': 0.0,
                'error': str(e)
            }
    
    def compare_faces_deepface(self, img1, img2):
        """Advanced face comparison using DeepFace"""
        try:
            result = DeepFace.verify(
                img1_path=img1,
                img2_path=img2,
                model_name=self.default_model,
                enforce_detection=True
            )
            
            return {
                'is_match': result['verified'],
                'distance': result['distance'],
                'similarity': 1 - result['distance'],
                'confidence': (1 - result['distance']) if result['verified'] else 0.0,
                'threshold': result['threshold']
            }
            
        except Exception as e:
            return {
                'is_match': False,
                'similarity': 0.0,
                'distance': 1.0,
                'confidence': 0.0,
                'error': str(e)
            }
    
    def verify_face(self, stored_encoding, live_image_data):
        """Main face verification function"""
        try:
            # Preprocess live image
            live_image = self.preprocess_image(live_image_data)
            if live_image is None:
                return {
                    'success': False,
                    'error': 'Failed to preprocess live image'
                }
            
            # Detect face in live image
            face_location, error = self.detect_faces(live_image)
            if error:
                return {
                    'success': False,
                    'error': error
                }
            
            # Extract encoding from live image
            live_encoding, error = self.extract_face_encoding(live_image, face_location)
            if error:
                return {
                    'success': False,
                    'error': error
                }
            
            # Parse stored encoding
            if isinstance(stored_encoding, str):
                try:
                    stored_encoding = json.loads(stored_encoding)
                    stored_encoding = np.array(stored_encoding)
                except:
                    return {
                        'success': False,
                        'error': 'Invalid stored face encoding format'
                    }
            
            # Compare faces
            comparison_result = self.compare_faces_basic(stored_encoding, live_encoding)
            
            # Additional quality checks
            quality_score = self.assess_image_quality(live_image, face_location)
            
            # Final verification decision
            is_verified = (
                comparison_result['is_match'] and 
                comparison_result['confidence'] >= self.confidence_threshold and
                quality_score >= 0.6
            )
            
            return {
                'success': True,
                'verified': is_verified,
                'confidence': comparison_result['confidence'],
                'similarity': comparison_result['similarity'],
                'quality_score': quality_score,
                'details': {
                    'face_detected': True,
                    'encoding_extracted': True,
                    'comparison_completed': True
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Face verification failed: {str(e)}'
            }
    
    def assess_image_quality(self, image, face_location):
        """Assess the quality of the face image"""
        try:
            top, right, bottom, left = face_location
            face_image = image[top:bottom, left:right]
            
            # Check image size
            height, width = face_image.shape[:2]
            size_score = min(1.0, (height * width) / (100 * 100))  # Minimum 100x100
            
            # Check brightness
            gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
            brightness = np.mean(gray) / 255.0
            brightness_score = 1.0 - abs(brightness - 0.5) * 2  # Optimal around 0.5
            
            # Check contrast
            contrast = np.std(gray) / 255.0
            contrast_score = min(1.0, contrast * 4)  # Higher contrast is better
            
            # Check blur (Laplacian variance)
            blur_score = min(1.0, cv2.Laplacian(gray, cv2.CV_64F).var() / 1000)
            
            # Combined quality score
            quality_score = (size_score + brightness_score + contrast_score + blur_score) / 4
            
            return quality_score
            
        except Exception as e:
            print(f"Error assessing image quality: {str(e)}")
            return 0.5  # Default moderate quality
    
    def encode_face_for_storage(self, image_data):
        """Encode face for database storage"""
        try:
            # Preprocess image
            image = self.preprocess_image(image_data)
            if image is None:
                return None, "Failed to preprocess image"
            
            # Detect face
            face_location, error = self.detect_faces(image)
            if error:
                return None, error
            
            # Extract encoding
            encoding, error = self.extract_face_encoding(image, face_location)
            if error:
                return None, error
            
            # Convert to JSON-serializable format
            encoding_json = json.dumps(encoding.tolist())
            
            return encoding_json, None
            
        except Exception as e:
            return None, f"Face encoding for storage failed: {str(e)}"
    
    def batch_verify_faces(self, stored_encodings, live_image_data):
        """Verify face against multiple stored encodings"""
        try:
            results = []
            
            for i, stored_encoding in enumerate(stored_encodings):
                result = self.verify_face(stored_encoding, live_image_data)
                result['encoding_index'] = i
                results.append(result)
            
            # Find best match
            successful_results = [r for r in results if r['success'] and r.get('verified', False)]
            
            if successful_results:
                best_match = max(successful_results, key=lambda x: x['confidence'])
                return {
                    'success': True,
                    'best_match': best_match,
                    'all_results': results
                }
            else:
                return {
                    'success': False,
                    'error': 'No matching face found',
                    'all_results': results
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Batch verification failed: {str(e)}'
            }

# Utility functions for face recognition
def create_face_database_entry(voter_id, image_data):
    """Create a face database entry for a voter"""
    face_system = FaceVerificationSystem()
    encoding, error = face_system.encode_face_for_storage(image_data)
    
    if error:
        return None, error
    
    return {
        'voter_id': voter_id,
        'face_encoding': encoding,
        'created_at': np.datetime64('now').isoformat()
    }, None

# Example usage and testing
if __name__ == "__main__":
    face_system = FaceVerificationSystem()
    print("Face Recognition System initialized successfully!")
    print(f"Using model: {face_system.default_model}")
    print(f"Verification threshold: {face_system.verification_threshold}")
    print("Ready to process face verification requests...")
