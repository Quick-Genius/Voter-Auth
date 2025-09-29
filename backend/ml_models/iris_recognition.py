import cv2
import numpy as np
import base64
import io
from PIL import Image
import json
import math

# Try to import optional libraries with fallbacks
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    print("⚠️  mediapipe library not available, using OpenCV fallback")

try:
    from scipy.spatial.distance import hamming
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    print("⚠️  scipy library not available, using basic distance calculation")

try:
    from skimage import feature, filters, morphology
    from skimage.transform import resize
    SKIMAGE_AVAILABLE = True
except ImportError:
    SKIMAGE_AVAILABLE = False
    print("⚠️  skimage library not available, using basic image processing")

class IrisRecognitionSystem:
    """Advanced iris recognition system for voter authentication"""
    
    def __init__(self):
        # Initialize MediaPipe if available
        if MEDIAPIPE_AVAILABLE:
            self.mp_face_mesh = mp.solutions.face_mesh
            self.face_mesh = self.mp_face_mesh.FaceMesh(
                static_image_mode=True,
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5
            )
            
            # Iris landmarks indices for MediaPipe
            self.LEFT_IRIS = [474, 475, 476, 477]
            self.RIGHT_IRIS = [469, 470, 471, 472]
        else:
            self.mp_face_mesh = None
            self.face_mesh = None
            self.LEFT_IRIS = None
            self.RIGHT_IRIS = None
        
        # Iris recognition parameters
        self.iris_radius_range = (20, 80)  # Min and max iris radius in pixels
        self.pupil_radius_range = (8, 40)   # Min and max pupil radius in pixels
        self.template_size = (64, 512)      # Normalized iris template size
        
        # Verification threshold
        self.verification_threshold = 0.3   # Hamming distance threshold
        
    def preprocess_image(self, image_data):
        """Preprocess image for iris recognition"""
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
            
            # Convert to RGB for MediaPipe
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            return rgb_image, image
            
        except Exception as e:
            print(f"Error preprocessing image: {str(e)}")
            return None, None
    
    def detect_eyes_mediapipe(self, rgb_image):
        """Detect eyes using MediaPipe Face Mesh"""
        try:
            results = self.face_mesh.process(rgb_image)
            
            if not results.multi_face_landmarks:
                return None, "No face detected in the image"
            
            face_landmarks = results.multi_face_landmarks[0]
            
            # Get image dimensions
            h, w = rgb_image.shape[:2]
            
            # Extract iris landmarks
            left_iris_points = []
            right_iris_points = []
            
            for idx in self.LEFT_IRIS:
                landmark = face_landmarks.landmark[idx]
                x = int(landmark.x * w)
                y = int(landmark.y * h)
                left_iris_points.append((x, y))
            
            for idx in self.RIGHT_IRIS:
                landmark = face_landmarks.landmark[idx]
                x = int(landmark.x * w)
                y = int(landmark.y * h)
                right_iris_points.append((x, y))
            
            # Calculate iris centers and radii
            left_center = self.calculate_center(left_iris_points)
            right_center = self.calculate_center(right_iris_points)
            
            left_radius = self.calculate_radius(left_iris_points, left_center)
            right_radius = self.calculate_radius(right_iris_points, right_center)
            
            return {
                'left_eye': {
                    'center': left_center,
                    'radius': left_radius,
                    'landmarks': left_iris_points
                },
                'right_eye': {
                    'center': right_center,
                    'radius': right_radius,
                    'landmarks': right_iris_points
                }
            }, None
            
        except Exception as e:
            return None, f"Eye detection failed: {str(e)}"
    
    def calculate_center(self, points):
        """Calculate center point from a list of points"""
        x_coords = [p[0] for p in points]
        y_coords = [p[1] for p in points]
        center_x = sum(x_coords) // len(x_coords)
        center_y = sum(y_coords) // len(y_coords)
        return (center_x, center_y)
    
    def calculate_radius(self, points, center):
        """Calculate average radius from center to points"""
        distances = []
        for point in points:
            dist = math.sqrt((point[0] - center[0])**2 + (point[1] - center[1])**2)
            distances.append(dist)
        return int(sum(distances) / len(distances))
    
    def extract_iris_region(self, image, eye_info):
        """Extract iris region from the image"""
        try:
            center = eye_info['center']
            radius = max(eye_info['radius'], 30)  # Minimum radius
            
            # Define extraction region (larger than iris for context)
            extraction_radius = int(radius * 1.5)
            
            x1 = max(0, center[0] - extraction_radius)
            y1 = max(0, center[1] - extraction_radius)
            x2 = min(image.shape[1], center[0] + extraction_radius)
            y2 = min(image.shape[0], center[1] + extraction_radius)
            
            # Extract region
            iris_region = image[y1:y2, x1:x2]
            
            if iris_region.size == 0:
                return None, "Failed to extract iris region"
            
            # Convert to grayscale if needed
            if len(iris_region.shape) == 3:
                iris_region = cv2.cvtColor(iris_region, cv2.COLOR_RGB2GRAY)
            
            return iris_region, None
            
        except Exception as e:
            return None, f"Iris extraction failed: {str(e)}"
    
    def normalize_iris(self, iris_image):
        """Normalize iris image to standard polar coordinates"""
        try:
            # Resize to standard size
            normalized = resize(iris_image, (64, 64), anti_aliasing=True)
            
            # Apply histogram equalization
            normalized = cv2.equalizeHist((normalized * 255).astype(np.uint8))
            
            # Convert to polar coordinates (simplified)
            h, w = normalized.shape
            center = (w // 2, h // 2)
            
            # Create polar transformation
            polar_image = cv2.warpPolar(
                normalized, 
                self.template_size, 
                center, 
                min(h, w) // 2, 
                cv2.WARP_POLAR_LINEAR
            )
            
            return polar_image
            
        except Exception as e:
            print(f"Iris normalization failed: {str(e)}")
            return iris_image  # Return original if normalization fails
    
    def extract_iris_features(self, normalized_iris):
        """Extract features from normalized iris image"""
        try:
            # Apply Gabor filters for texture analysis
            features = []
            
            # Multiple Gabor filter orientations
            orientations = [0, 45, 90, 135]
            frequencies = [0.1, 0.3, 0.5]
            
            for orientation in orientations:
                for frequency in frequencies:
                    # Apply Gabor filter
                    real, _ = filters.gabor(
                        normalized_iris, 
                        frequency=frequency, 
                        theta=np.deg2rad(orientation)
                    )
                    
                    # Extract statistical features
                    features.extend([
                        np.mean(real),
                        np.std(real),
                        np.max(real),
                        np.min(real)
                    ])
            
            # Add LBP (Local Binary Pattern) features
            lbp = feature.local_binary_pattern(
                normalized_iris, 
                P=8, 
                R=1, 
                method='uniform'
            )
            
            # LBP histogram
            lbp_hist, _ = np.histogram(lbp.ravel(), bins=10)
            features.extend(lbp_hist.tolist())
            
            return np.array(features)
            
        except Exception as e:
            print(f"Feature extraction failed: {str(e)}")
            return np.array([])
    
    def create_iris_template(self, iris_image):
        """Create binary iris template using advanced techniques"""
        try:
            # Normalize iris
            normalized = self.normalize_iris(iris_image)
            
            # Apply multiple filters
            # 1. Gabor filter bank
            gabor_responses = []
            for theta in range(0, 180, 30):
                for frequency in [0.1, 0.3]:
                    real, _ = filters.gabor(
                        normalized, 
                        frequency=frequency, 
                        theta=np.deg2rad(theta)
                    )
                    gabor_responses.append(real)
            
            # 2. Create binary template
            template = np.zeros_like(normalized, dtype=np.uint8)
            
            for response in gabor_responses:
                # Threshold response
                binary_response = (response > np.mean(response)).astype(np.uint8)
                template = np.bitwise_xor(template, binary_response)
            
            # 3. Create mask for valid regions
            mask = np.ones_like(template, dtype=np.uint8)
            
            # Remove border regions
            border_size = 5
            mask[:border_size, :] = 0
            mask[-border_size:, :] = 0
            mask[:, :border_size] = 0
            mask[:, -border_size:] = 0
            
            return template, mask
            
        except Exception as e:
            print(f"Template creation failed: {str(e)}")
            return None, None
    
    def compare_iris_templates(self, template1, mask1, template2, mask2):
        """Compare two iris templates using Hamming distance"""
        try:
            # Ensure templates are same size
            if template1.shape != template2.shape:
                template2 = cv2.resize(template2, template1.shape[::-1])
                mask2 = cv2.resize(mask2, template1.shape[::-1])
            
            # Apply masks
            valid_pixels = np.logical_and(mask1, mask2)
            
            if np.sum(valid_pixels) == 0:
                return 1.0  # Maximum distance if no valid pixels
            
            # Calculate Hamming distance
            t1_valid = template1[valid_pixels]
            t2_valid = template2[valid_pixels]
            
            # Convert to binary strings
            t1_binary = ''.join(t1_valid.astype(str))
            t2_binary = ''.join(t2_valid.astype(str))
            
            # Calculate normalized Hamming distance
            if len(t1_binary) == 0:
                return 1.0
            
            distance = hamming(list(t1_binary), list(t2_binary))
            
            return distance
            
        except Exception as e:
            print(f"Template comparison failed: {str(e)}")
            return 1.0  # Return maximum distance on error
    
    def verify_iris(self, stored_template_data, live_image_data):
        """Main iris verification function"""
        try:
            # Preprocess live image
            rgb_image, bgr_image = self.preprocess_image(live_image_data)
            if rgb_image is None:
                return {
                    'success': False,
                    'error': 'Failed to preprocess live image'
                }
            
            # Detect eyes
            eye_info, error = self.detect_eyes_mediapipe(rgb_image)
            if error:
                return {
                    'success': False,
                    'error': error
                }
            
            # Process both eyes
            results = {}
            
            for eye_name in ['left_eye', 'right_eye']:
                if eye_name in eye_info:
                    # Extract iris region
                    iris_region, error = self.extract_iris_region(
                        cv2.cvtColor(rgb_image, cv2.COLOR_RGB2GRAY), 
                        eye_info[eye_name]
                    )
                    
                    if error:
                        results[eye_name] = {
                            'success': False,
                            'error': error
                        }
                        continue
                    
                    # Create template
                    template, mask = self.create_iris_template(iris_region)
                    
                    if template is None:
                        results[eye_name] = {
                            'success': False,
                            'error': 'Failed to create iris template'
                        }
                        continue
                    
                    # Parse stored template
                    try:
                        stored_data = json.loads(stored_template_data) if isinstance(stored_template_data, str) else stored_template_data
                        stored_template = np.array(stored_data.get(f'{eye_name}_template', []))
                        stored_mask = np.array(stored_data.get(f'{eye_name}_mask', []))
                        
                        if stored_template.size == 0:
                            results[eye_name] = {
                                'success': False,
                                'error': 'No stored template found'
                            }
                            continue
                        
                    except Exception as e:
                        results[eye_name] = {
                            'success': False,
                            'error': f'Invalid stored template: {str(e)}'
                        }
                        continue
                    
                    # Compare templates
                    distance = self.compare_iris_templates(
                        stored_template, stored_mask, template, mask
                    )
                    
                    # Calculate similarity and verification result
                    similarity = 1.0 - distance
                    is_verified = distance < self.verification_threshold
                    
                    results[eye_name] = {
                        'success': True,
                        'verified': is_verified,
                        'similarity': similarity,
                        'distance': distance,
                        'confidence': similarity if is_verified else 0.0
                    }
            
            # Overall verification result
            verified_eyes = [r for r in results.values() if r.get('success') and r.get('verified')]
            
            if verified_eyes:
                best_result = max(verified_eyes, key=lambda x: x['confidence'])
                overall_verified = True
                overall_confidence = best_result['confidence']
            else:
                overall_verified = False
                overall_confidence = 0.0
            
            return {
                'success': True,
                'verified': overall_verified,
                'confidence': overall_confidence,
                'eye_results': results,
                'details': {
                    'eyes_detected': len(eye_info),
                    'eyes_processed': len([r for r in results.values() if r.get('success')]),
                    'eyes_verified': len(verified_eyes)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Iris verification failed: {str(e)}'
            }
    
    def encode_iris_for_storage(self, image_data):
        """Encode iris data for database storage"""
        try:
            # Preprocess image
            rgb_image, bgr_image = self.preprocess_image(image_data)
            if rgb_image is None:
                return None, "Failed to preprocess image"
            
            # Detect eyes
            eye_info, error = self.detect_eyes_mediapipe(rgb_image)
            if error:
                return None, error
            
            # Process both eyes
            storage_data = {}
            
            for eye_name in ['left_eye', 'right_eye']:
                if eye_name in eye_info:
                    # Extract iris region
                    iris_region, error = self.extract_iris_region(
                        cv2.cvtColor(rgb_image, cv2.COLOR_RGB2GRAY), 
                        eye_info[eye_name]
                    )
                    
                    if not error:
                        # Create template
                        template, mask = self.create_iris_template(iris_region)
                        
                        if template is not None:
                            storage_data[f'{eye_name}_template'] = template.tolist()
                            storage_data[f'{eye_name}_mask'] = mask.tolist()
            
            if not storage_data:
                return None, "Failed to extract iris templates from any eye"
            
            # Convert to JSON string
            storage_json = json.dumps(storage_data)
            
            return storage_json, None
            
        except Exception as e:
            return None, f"Iris encoding for storage failed: {str(e)}"
    
    def assess_iris_quality(self, iris_image):
        """Assess the quality of iris image"""
        try:
            # Check image size
            h, w = iris_image.shape[:2]
            size_score = min(1.0, (h * w) / (50 * 50))  # Minimum 50x50
            
            # Check contrast
            contrast = np.std(iris_image) / 255.0
            contrast_score = min(1.0, contrast * 3)
            
            # Check focus (using Laplacian variance)
            focus_score = min(1.0, cv2.Laplacian(iris_image, cv2.CV_64F).var() / 500)
            
            # Check brightness distribution
            hist = cv2.calcHist([iris_image], [0], None, [256], [0, 256])
            brightness_score = 1.0 - abs(np.argmax(hist) - 128) / 128.0
            
            # Combined quality score
            quality_score = (size_score + contrast_score + focus_score + brightness_score) / 4
            
            return quality_score
            
        except Exception as e:
            print(f"Error assessing iris quality: {str(e)}")
            return 0.5  # Default moderate quality

# Utility functions
def create_iris_database_entry(voter_id, image_data):
    """Create an iris database entry for a voter"""
    iris_system = IrisRecognitionSystem()
    template_data, error = iris_system.encode_iris_for_storage(image_data)
    
    if error:
        return None, error
    
    return {
        'voter_id': voter_id,
        'iris_template': template_data,
        'created_at': np.datetime64('now').isoformat()
    }, None

# Example usage and testing
if __name__ == "__main__":
    iris_system = IrisRecognitionSystem()
    print("Iris Recognition System initialized successfully!")
    print(f"Verification threshold: {iris_system.verification_threshold}")
    print(f"Template size: {iris_system.template_size}")
    print("Ready to process iris verification requests...")
