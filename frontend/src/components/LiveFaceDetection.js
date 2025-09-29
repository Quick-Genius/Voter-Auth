import React, { useRef, useEffect, useState } from 'react';
import { Box, Typography, LinearProgress, Alert, Button } from '@mui/material';
import { FaceDetection } from '@mediapipe/face_detection';
import { Camera } from '@mediapipe/camera_utils';

const LiveFaceDetection = ({ onFaceDetected, onLivenessVerified }) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [isDetecting, setIsDetecting] = useState(false);
  const [confidence, setConfidence] = useState(0);
  const [livenessScore, setLivenessScore] = useState(0);
  const [status, setStatus] = useState('Initializing camera...');
  const [blinkCount, setBlinkCount] = useState(0);
  const [headMovement, setHeadMovement] = useState(false);
  const [hasTriggeredCapture, setHasTriggeredCapture] = useState(false);
  
  // Face detection state
  const [faceDetection, setFaceDetection] = useState(null);
  const [camera, setCamera] = useState(null);
  const [lastFacePosition, setLastFacePosition] = useState(null);
  const [eyeClosedFrames, setEyeClosedFrames] = useState(0);
  const [currentDetections, setCurrentDetections] = useState(null);

  useEffect(() => {
    initializeFaceDetection();
    return () => {
      if (camera) {
        camera.stop();
      }
    };
  }, []);

  const initializeFaceDetection = async () => {
    try {
      // Initialize MediaPipe Face Detection
      const faceDetector = new FaceDetection({
        locateFile: (file) => {
          return `https://cdn.jsdelivr.net/npm/@mediapipe/face_detection/${file}`;
        }
      });

      faceDetector.setOptions({
        model: 'short',
        minDetectionConfidence: 0.5,
      });

      faceDetector.onResults(onFaceDetectionResults);
      setFaceDetection(faceDetector);

      // Initialize camera
      if (videoRef.current) {
        const cam = new Camera(videoRef.current, {
          onFrame: async () => {
            if (faceDetector && videoRef.current) {
              await faceDetector.send({ image: videoRef.current });
            }
          },
          width: 640,
          height: 480
        });
        
        await cam.start();
        setCamera(cam);
        setStatus('Camera ready - Position your face in the frame');
      }
    } catch (error) {
      console.error('Face detection initialization failed:', error);
      setStatus('Camera initialization failed');
    }
  };

  const onFaceDetectionResults = (results) => {
    const canvas = canvasRef.current;
    const video = videoRef.current;
    
    if (!canvas || !video) return;

    const ctx = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw video frame
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    if (results.detections && results.detections.length > 0) {
      setCurrentDetections(results.detections); // ADD THIS LINE
      const detection = results.detections[0];
      const bbox = detection.boundingBox;
      const confidence = detection.score ? detection.score[0] : 0;
      
      setConfidence(confidence);

      // Draw bounding box
      ctx.strokeStyle = confidence > 0.8 ? '#4CAF50' : '#FF9800';
      ctx.lineWidth = 3;
      ctx.strokeRect(
        bbox.xCenter * canvas.width - (bbox.width * canvas.width) / 2,
        bbox.yCenter * canvas.height - (bbox.height * canvas.height) / 2,
        bbox.width * canvas.width,
        bbox.height * canvas.height
      );

      // Check liveness
      checkLiveness(detection);

      // Only auto-capture if strict conditions are met and not already detecting
      if (confidence > 0.85 && livenessScore > 0.5 && blinkCount > 0 && !isDetecting && !hasTriggeredCapture) {
        setHasTriggeredCapture(true);
        // Add a small delay to ensure stable detection
        setTimeout(() => {
          if (confidence > 0.85 && livenessScore > 0.5 && !isDetecting) {
            autoCaptureFace();
          }
        }, 3000);
      }

      setStatus(`Face detected - Confidence: ${(confidence * 100).toFixed(1)}%`);
    } else {
      setStatus('No face detected - Please position your face in the frame');
      setConfidence(0);
    }
  };

  const checkLiveness = (detection) => {
    // Simple liveness detection based on face movement and size changes
    const currentPosition = {
      x: detection.boundingBox.xCenter,
      y: detection.boundingBox.yCenter,
      size: detection.boundingBox.width * detection.boundingBox.height
    };

    if (lastFacePosition) {
      const movement = Math.abs(currentPosition.x - lastFacePosition.x) + 
                     Math.abs(currentPosition.y - lastFacePosition.y);
      
      const sizeChange = Math.abs(currentPosition.size - lastFacePosition.size);

      if (movement > 0.02 || sizeChange > 0.01) {
        setHeadMovement(true);
        setLivenessScore(prev => Math.min(prev + 0.1, 1.0));
      }

      // Simple blink detection (based on face size fluctuation)
      if (sizeChange > 0.005) {
        setEyeClosedFrames(prev => prev + 1);
        if (eyeClosedFrames > 3) {
          setBlinkCount(prev => prev + 1);
          setEyeClosedFrames(0);
          setLivenessScore(prev => Math.min(prev + 0.2, 1.0));
        }
      }
    }

    setLastFacePosition(currentPosition);
  };

  const getCurrentDetections = async () => {
    return currentDetections;
  };

  const autoCaptureFace = async () => {
    if (isDetecting) return;
    
    // Strict validation before capture
    if (confidence < 0.85) {
      setStatus('Face confidence too low - Please position your face clearly');
      return;
    }
    
    if (livenessScore < 0.5) {
      setStatus('Liveness check failed - Please blink and move your head slightly');
      return;
    }
    
    setIsDetecting(true);
    setStatus('Capturing face for verification...');

    try {
      // Capture high-quality face region
      const canvas = document.createElement('canvas');
      const video = videoRef.current;
      
      // Get the detected face bounding box for cropping
      const detections = await getCurrentDetections();
      if (detections && detections.length > 0) {
        const bbox = detections[0].boundingBox;
        
        // Crop to face region with padding
        const padding = 0.2; // 20% padding around face
        const faceWidth = bbox.width * video.videoWidth;
        const faceHeight = bbox.height * video.videoHeight;
        const faceX = (bbox.xCenter * video.videoWidth) - (faceWidth / 2);
        const faceY = (bbox.yCenter * video.videoHeight) - (faceHeight / 2);
        
        // Add padding
        const cropX = Math.max(0, faceX - (faceWidth * padding));
        const cropY = Math.max(0, faceY - (faceHeight * padding));
        const cropWidth = Math.min(video.videoWidth - cropX, faceWidth * (1 + 2 * padding));
        const cropHeight = Math.min(video.videoHeight - cropY, faceHeight * (1 + 2 * padding));
        
        // Set canvas to optimal face recognition size
        canvas.width = 224; // Standard face recognition input size
        canvas.height = 224;
        
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, cropX, cropY, cropWidth, cropHeight, 0, 0, 224, 224);
      } else {
        // Fallback to full frame
        canvas.width = 224;
        canvas.height = 224;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, 224, 224);
      }
      
      const imageData = canvas.toDataURL('image/jpeg', 0.95); // Higher quality
      
      // Call parent callback with captured image
      if (onFaceDetected) {
        await onFaceDetected(imageData);
      }

      if (onLivenessVerified) {
        onLivenessVerified({
          score: livenessScore,
          blinkCount,
          headMovement,
          confidence
        });
      }

      setStatus('Face captured and sent for verification!');
    } catch (error) {
      console.error('Face capture failed:', error);
      setStatus('Face capture failed - Please try again');
      setIsDetecting(false);
    }
  };

  const resetDetection = () => {
    setBlinkCount(0);
    setHeadMovement(false);
    setLivenessScore(0);
    setConfidence(0);
    setHasTriggeredCapture(false); // Add this line
    setIsDetecting(false);
    setStatus('Position your face in the frame');
  };

  return (
    <Box sx={{ position: 'relative', width: '100%', maxWidth: 640 }}>
      {/* Video and Canvas */}
      <Box sx={{ position: 'relative', borderRadius: 2, overflow: 'hidden' }}>
        <video
          ref={videoRef}
          style={{
            width: '100%',
            height: 'auto',
            display: 'block'
          }}
          playsInline
          muted
        />
        <canvas
          ref={canvasRef}
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            pointerEvents: 'none'
          }}
        />
      </Box>

      {/* Status and Progress */}
      <Box sx={{ mt: 2 }}>
        <Typography variant="body2" color="textSecondary" gutterBottom>
          {status}
        </Typography>
        
        {/* Confidence Progress */}
        <Box sx={{ mb: 1 }}>
          <Typography variant="caption">
            Face Confidence: {(confidence * 100).toFixed(1)}%
          </Typography>
          <LinearProgress 
            variant="determinate" 
            value={confidence * 100} 
            color={confidence > 0.8 ? 'success' : 'warning'}
          />
        </Box>

        {/* Liveness Progress */}
        <Box sx={{ mb: 1 }}>
          <Typography variant="caption">
            Liveness Score: {(livenessScore * 100).toFixed(1)}%
          </Typography>
          <LinearProgress 
            variant="determinate" 
            value={livenessScore * 100} 
            color={livenessScore > 0.7 ? 'success' : 'info'}
          />
        </Box>

        {/* Liveness Indicators */}
        <Box sx={{ display: 'flex', gap: 2, mt: 1 }}>
          <Typography variant="caption" color={blinkCount > 0 ? 'success.main' : 'text.secondary'}>
            👁️ Blinks: {blinkCount}
          </Typography>
          <Typography variant="caption" color={headMovement ? 'success.main' : 'text.secondary'}>
            📱 Head Movement: {headMovement ? '✓' : '✗'}
          </Typography>
        </Box>

        {/* Instructions */}
        {confidence < 0.5 && (
          <Alert severity="info" sx={{ mt: 2 }}>
            Please position your face clearly in the frame for automatic detection
          </Alert>
        )}

        {confidence > 0.5 && livenessScore < 0.3 && (
          <Alert severity="warning" sx={{ mt: 2 }}>
            Please blink and move your head slightly to verify liveness
          </Alert>
        )}

        {confidence > 0.8 && livenessScore > 0.7 && !isDetecting && (
          <Alert severity="success" sx={{ mt: 2 }}>
            Ready for automatic verification!
          </Alert>
        )}

        {/* Action Buttons */}
        <Box sx={{ display: 'flex', gap: 2, mt: 2, justifyContent: 'center' }}>
          <Button 
            variant="outlined" 
            onClick={resetDetection}
            size="small"
          >
            Reset Detection
          </Button>
          
          {confidence > 0.7 && livenessScore > 0.3 && (
            <Button 
              variant="contained" 
              onClick={autoCaptureFace}
              disabled={isDetecting || confidence < 0.7}
              size="small"
            >
              {isDetecting ? 'Verifying...' : 'Capture Face'}
            </Button>
          )}
        </Box>
      </Box>
    </Box>
  );
};

export default LiveFaceDetection;
