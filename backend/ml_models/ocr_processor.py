import cv2
import numpy as np
import re
import base64
from PIL import Image
import io
import json

# Try to import OCR libraries with fallbacks
try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False
    print("  pytesseract library not available, using basic text extraction")

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    print("  easyocr library not available, using basic text extraction")

class VoterIDOCR:
    """OCR processor for Indian Voter ID cards"""
    
    def __init__(self):
        if EASYOCR_AVAILABLE:
            self.reader = easyocr.Reader(['en', 'hi'])
        else:
            self.reader = None
        
        # Common patterns in Indian Voter IDs
        self.voter_id_pattern = r'[A-Z]{3}[0-9]{7}'  # Standard voter ID format
        self.name_keywords = ['name', 'नाम']
        self.id_keywords = ['electors', 'photo', 'identity', 'card']
        
    def preprocess_image(self, image_data):
        """Preprocess image for better OCR results"""
        try:
            # Decode base64 image
            if isinstance(image_data, str):
                image_bytes = base64.b64decode(image_data.split(',')[1])
                image = Image.open(io.BytesIO(image_bytes))
                image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            else:
                image = image_data
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Morphological operations to clean up the image
            kernel = np.ones((2, 2), np.uint8)
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            return cleaned
            
        except Exception as e:
            print(f"Error in image preprocessing: {str(e)}")
            return None
    
    def extract_text_tesseract(self, image):
        """Extract text using Tesseract OCR"""
        try:
            # Configure Tesseract for better accuracy
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 '
            
            text = pytesseract.image_to_string(image, config=custom_config)
            return text.strip()
            
        except Exception as e:
            print(f"Error in Tesseract OCR: {str(e)}")
            return ""
    
    def extract_text_easyocr(self, image):
        """Extract text using EasyOCR"""
        try:
            results = self.reader.readtext(image)
            
            # Combine all detected text
            extracted_text = []
            for (bbox, text, confidence) in results:
                if confidence > 0.5:  # Filter low confidence detections
                    extracted_text.append(text)
            
            return ' '.join(extracted_text)
            
        except Exception as e:
            print(f"Error in EasyOCR: {str(e)}")
            return ""
    
    def extract_voter_id(self, text):
        """Extract voter ID from text using regex patterns"""
        try:
            # Clean the text
            cleaned_text = re.sub(r'[^\w\s]', '', text.upper())
            
            # Search for voter ID pattern
            voter_id_matches = re.findall(self.voter_id_pattern, cleaned_text)
            
            if voter_id_matches:
                return voter_id_matches[0]
            
            # Alternative patterns for different formats
            alt_patterns = [
                r'[A-Z]{2,4}[0-9]{6,8}',  # Alternative format
                r'[A-Z]+[0-9]+',          # General alphanumeric
            ]
            
            for pattern in alt_patterns:
                matches = re.findall(pattern, cleaned_text)
                for match in matches:
                    if len(match) >= 8 and len(match) <= 12:  # Reasonable length
                        return match
            
            return None
            
        except Exception as e:
            print(f"Error extracting voter ID: {str(e)}")
            return None
    
    def extract_name(self, text):
        """Extract name from voter ID text"""
        try:
            lines = text.split('\n')
            
            # Look for lines that might contain the name
            potential_names = []
            
            for line in lines:
                line = line.strip()
                if len(line) > 3 and len(line) < 50:  # Reasonable name length
                    # Check if line contains mostly alphabetic characters
                    if sum(c.isalpha() or c.isspace() for c in line) / len(line) > 0.7:
                        # Avoid lines with common keywords
                        if not any(keyword.lower() in line.lower() for keyword in 
                                 ['election', 'commission', 'india', 'card', 'identity']):
                            potential_names.append(line)
            
            # Return the most likely name (usually the longest valid string)
            if potential_names:
                return max(potential_names, key=len)
            
            return None
            
        except Exception as e:
            print(f"Error extracting name: {str(e)}")
            return None
    
    def process_voter_id_card(self, image_data):
        """Main function to process voter ID card and extract information"""
        try:
            # Preprocess image
            processed_image = self.preprocess_image(image_data)
            if processed_image is None:
                return {
                    'success': False,
                    'error': 'Failed to preprocess image'
                }
            
            # Extract text using both OCR methods
            tesseract_text = self.extract_text_tesseract(processed_image)
            easyocr_text = self.extract_text_easyocr(processed_image)
            
            # Combine results
            combined_text = f"{tesseract_text}\n{easyocr_text}"
            
            # Extract voter ID and name
            voter_id = self.extract_voter_id(combined_text)
            name = self.extract_name(combined_text)
            
            # Validate results
            if not voter_id:
                return {
                    'success': False,
                    'error': 'Could not extract voter ID from image',
                    'raw_text': combined_text[:200]  # First 200 chars for debugging
                }
            
            return {
                'success': True,
                'voter_id': voter_id,
                'name': name,
                'raw_text': combined_text,
                'confidence': self.calculate_confidence(voter_id, name, combined_text)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'OCR processing failed: {str(e)}'
            }
    
    def calculate_confidence(self, voter_id, name, text):
        """Calculate confidence score for OCR results"""
        confidence = 0.0
        
        # Voter ID format confidence
        if voter_id and re.match(self.voter_id_pattern, voter_id):
            confidence += 0.5
        elif voter_id:
            confidence += 0.3
        
        # Name extraction confidence
        if name and len(name) > 3:
            confidence += 0.3
        
        # Text quality confidence
        if len(text) > 50:  # Sufficient text extracted
            confidence += 0.2
        
        return min(confidence, 1.0)
    
    def validate_voter_id_format(self, voter_id):
        """Validate if voter ID follows standard format"""
        if not voter_id:
            return False
        
        # Check standard format: 3 letters + 7 digits
        if re.match(self.voter_id_pattern, voter_id):
            return True
        
        # Check alternative formats
        if len(voter_id) >= 8 and len(voter_id) <= 12:
            if re.match(r'^[A-Z]+[0-9]+$', voter_id):
                return True
        
        return False

# Example usage and testing
if __name__ == "__main__":
    ocr_processor = VoterIDOCR()
    
    # Test with sample data
    print("Voter ID OCR Processor initialized successfully!")
    print("Ready to process voter ID cards...")
