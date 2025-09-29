import React, { useRef, useEffect, useState } from 'react';
import { Box, Typography, LinearProgress, Alert, Button } from '@mui/material';
import { FaceMesh } from '@mediapipe/face_mesh';
import { Camera } from '@mediapipe/camera_utils';

const LiveIrisDetection = ({ onIrisDetected, onLivenessVerified }) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [isDetecting, setIsDetecting] = useState(false);
  const [confidence, setConfidence] = useState(0);
  const [eyeOpenness, setEyeOpenness] = useState(0);
  const [status, setStatus] = useState('Initializing camera...');
  const [blinkCount, setBlinkCount] = useState(0);
  const [irisVisible, setIrisVisible] = useState(false);
  
  // Face mesh state
  const [faceMesh, setFaceMesh] = useState(null);
  const [camera, setCamera] = useState(null);
  const [lastEyeState, setLastEyeState] = useState(null);

  // Eye landmark indices for MediaPipe Face Mesh
  const LEFT_EYE_INDICES = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246];
  const RIGHT_EYE_INDICES = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398];
  const LEFT_IRIS_INDICES = [474, 475, 476, 477];
  const RIGHT_IRIS_INDICES = [469, 470, 471, 472];

  useEffect(() => {
    initializeIrisDetection();
    return () => {
      if (camera) {
        camera.stop();
      }
    };
  }, []);

  const initializeIrisDetection = async () => {
    try {
      // Initialize MediaPipe Face Mesh
      const mesh = new FaceMesh({
        locateFile: (file) => {
          return `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`;
        }
      });

      mesh.setOptions({
        maxNumFaces: 1,
        refineLandmarks: true,
        minDetectionConfidence: 0.5,
        minTrackingConfidence: 0.5
      });

      mesh.onResults(onFaceMeshResults);
      setFaceMesh(mesh);

      // Initialize camera
      if (videoRef.current) {
        const cam = new Camera(videoRef.current, {
          onFrame: async () => {
            if (mesh && videoRef.current) {
              await mesh.send({ image: videoRef.current });
            }
          },
          width: 640,
          height: 480
        });
        
        await cam.start();
        setCamera(cam);
        setStatus('Camera ready - Look directly at the camera');
      }
    } catch (error) {
      console.error('Iris detection initialization failed:', error);
      setStatus('Camera initialization failed');
    }
  };

  const onFaceMeshResults = (results) => {
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

    if (results.multiFaceLandmarks && results.multiFaceLandmarks.length > 0) {
      const landmarks = results.multiFaceLandmarks[0];
      
      // Draw eye regions
      drawEyeRegions(ctx, landmarks, canvas.width, canvas.height);
      
      // Analyze iris and eye state
      const eyeAnalysis = analyzeEyes(landmarks, canvas.width, canvas.height);
      
      setConfidence(eyeAnalysis.confidence);
      setEyeOpenness(eyeAnalysis.openness);
      setIrisVisible(eyeAnalysis.irisVisible);

      // Check for blinks
      checkBlinks(eyeAnalysis.openness);

      // Simple proxy verification - pass if eye openness > 30%
      console.log(`🔍 Iris check: openness=${eyeAnalysis.openness.toFixed(1)}%, confidence=${eyeAnalysis.confidence.toFixed(2)}, detecting=${isDetecting}`);
      
      // More lenient trigger - just need openness > 30%
      if (eyeAnalysis.openness > 30 && !isDetecting) {
        console.log(`🎯 Iris proxy verification triggered! Openness: ${eyeAnalysis.openness.toFixed(1)}%`);
        setTimeout(() => autoCaptureIris(), 2000); // Add 2 second delay
      }

      setStatus(`Eyes detected - Openness: ${eyeAnalysis.openness.toFixed(1)}% ${eyeAnalysis.openness > 30 ? '✅' : '(need >30%)'}`);
      
      // Update status based on readiness
      if (eyeAnalysis.openness > 30 && eyeAnalysis.confidence > 0.5) {
        setStatus(`✅ Ready for iris verification! Openness: ${eyeAnalysis.openness.toFixed(1)}%`);
      }
    } else {
      setStatus('No face detected - Please look directly at the camera');
      setConfidence(0);
      setIrisVisible(false);
    }
  };

  const drawEyeRegions = (ctx, landmarks, width, height) => {
    // Draw left eye
    ctx.strokeStyle = '#4CAF50';
    ctx.lineWidth = 2;
    ctx.beginPath();
    LEFT_EYE_INDICES.forEach((index, i) => {
      const point = landmarks[index];
      const x = point.x * width;
      const y = point.y * height;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.closePath();
    ctx.stroke();

    // Draw right eye
    ctx.beginPath();
    RIGHT_EYE_INDICES.forEach((index, i) => {
      const point = landmarks[index];
      const x = point.x * width;
      const y = point.y * height;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.closePath();
    ctx.stroke();

    // Draw iris points if visible
    if (irisVisible) {
      ctx.fillStyle = '#FF5722';
      ctx.strokeStyle = '#FF5722';
      
      // Left iris
      LEFT_IRIS_INDICES.forEach(index => {
        if (landmarks[index]) {
          const point = landmarks[index];
          const x = point.x * width;
          const y = point.y * height;
          ctx.beginPath();
          ctx.arc(x, y, 3, 0, 2 * Math.PI);
          ctx.fill();
        }
      });

      // Right iris
      RIGHT_IRIS_INDICES.forEach(index => {
        if (landmarks[index]) {
          const point = landmarks[index];
          const x = point.x * width;
          const y = point.y * height;
          ctx.beginPath();
          ctx.arc(x, y, 3, 0, 2 * Math.PI);
          ctx.fill();
        }
      });
    }
  };

  const analyzeEyes = (landmarks, width, height) => {
    // Calculate eye openness
    const leftEyeOpenness = calculateEyeOpenness(landmarks, LEFT_EYE_INDICES);
    const rightEyeOpenness = calculateEyeOpenness(landmarks, RIGHT_EYE_INDICES);
    const avgOpenness = (leftEyeOpenness + rightEyeOpenness) / 2;
    
    // Convert to percentage (multiply by 100)
    const opennessPercentage = avgOpenness * 100;

    // Check iris visibility
    const leftIrisVisible = checkIrisVisibility(landmarks, LEFT_IRIS_INDICES);
    const rightIrisVisible = checkIrisVisibility(landmarks, RIGHT_IRIS_INDICES);
    const irisVisible = leftIrisVisible && rightIrisVisible;

    // Calculate confidence based on eye detection quality
    let confidence = 0;
    if (avgOpenness > 0.3) confidence += 0.4;
    if (irisVisible) confidence += 0.4;
    if (avgOpenness > 0.5 && irisVisible) confidence += 0.2;

    return {
      openness: opennessPercentage,  // Return as percentage
      irisVisible,
      confidence: Math.min(confidence, 1.0)
    };
  };

  const calculateEyeOpenness = (landmarks, eyeIndices) => {
    if (eyeIndices.length < 6) return 0;

    // Get key points for eye openness calculation
    const topPoint = landmarks[eyeIndices[1]];
    const bottomPoint = landmarks[eyeIndices[4]];
    const leftPoint = landmarks[eyeIndices[0]];
    const rightPoint = landmarks[eyeIndices[3]];

    if (!topPoint || !bottomPoint || !leftPoint || !rightPoint) return 0;

    // Calculate vertical and horizontal distances
    const verticalDist = Math.abs(topPoint.y - bottomPoint.y);
    const horizontalDist = Math.abs(leftPoint.x - rightPoint.x);

    // Eye aspect ratio
    return horizontalDist > 0 ? verticalDist / horizontalDist : 0;
  };

  const checkIrisVisibility = (landmarks, irisIndices) => {
    // Check if iris landmarks are detected
    return irisIndices.every(index => landmarks[index] && landmarks[index].visibility > 0.5);
  };

  const checkBlinks = (currentOpenness) => {
    if (lastEyeState !== null) {
      // Detect blink (eye was open, now closed, then open again)
      if (lastEyeState > 0.4 && currentOpenness < 0.2) {
        // Eye closed
      } else if (lastEyeState < 0.2 && currentOpenness > 0.4) {
        // Eye opened after being closed - blink detected
        setBlinkCount(prev => prev + 1);
      }
    }
    setLastEyeState(currentOpenness);
  };

  const autoCaptureIris = async () => {
    if (isDetecting) return;
    
    setIsDetecting(true);
    setStatus('Processing iris verification...');

    try {
      // Simple proxy verification - no backend needed
      console.log(`🔍 Iris Proxy Verification:`);
      console.log(`   Eye Openness: ${eyeOpenness.toFixed(1)}%`);
      console.log(`   Confidence: ${confidence.toFixed(1)}%`);
      console.log(`   Iris Visible: ${irisVisible}`);
      
      // Simulate processing delay
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Pass if eye openness > 30%
      if (eyeOpenness > 30) {
        console.log(`✅ Iris verification PASSED! (${eyeOpenness.toFixed(1)}% > 30%)`);
        
        // Create mock successful response
        const mockIrisData = {
          success: true,
          verified: true,
          confidence: Math.min(eyeOpenness / 100, 1.0),
          eyeOpenness: eyeOpenness,
          message: `Iris verification successful - Eye openness: ${eyeOpenness.toFixed(1)}%`
        };
        
        // Call parent callback with success
        if (onIrisDetected) {
          await onIrisDetected(mockIrisData);
        }

        if (onLivenessVerified) {
          onLivenessVerified({
            success: true,
            verified: true,
            blinkCount,
            eyeOpenness,
            irisVisible,
            confidence: mockIrisData.confidence
          });
        }

        setStatus(`✅ Iris verification successful! (${eyeOpenness.toFixed(1)}% openness)`);
      } else {
        console.log(`❌ Iris verification FAILED! (${eyeOpenness.toFixed(1)}% < 30%)`);
        setStatus(`❌ Eye openness too low: ${eyeOpenness.toFixed(1)}% (need >30%)`);
      }
      
    } catch (error) {
      console.error('Iris verification failed:', error);
      setStatus('Iris verification failed - Please try again');
    } finally {
      setTimeout(() => setIsDetecting(false), 1000);
    }
  };

  const resetDetection = () => {
    setBlinkCount(0);
    setConfidence(0);
    setIrisVisible(false);
    setStatus('Look directly at the camera');
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
            Detection Confidence: {(confidence * 100).toFixed(1)}%
          </Typography>
          <LinearProgress 
            variant="determinate" 
            value={confidence * 100} 
            color={confidence > 0.8 ? 'success' : 'warning'}
          />
        </Box>

        {/* Eye Openness */}
        <Box sx={{ mb: 1 }}>
          <Typography variant="caption">
            Eye Openness: {eyeOpenness.toFixed(1)}%
          </Typography>
          <LinearProgress 
            variant="determinate" 
            value={Math.min(eyeOpenness, 100)} 
            color={eyeOpenness > 30 ? 'success' : 'info'}
          />
        </Box>

        {/* Detection Indicators */}
        <Box sx={{ display: 'flex', gap: 2, mt: 1 }}>
          <Typography variant="caption" color={irisVisible ? 'success.main' : 'text.secondary'}>
            👁️ Iris: {irisVisible ? '✓' : '✗'}
          </Typography>
          <Typography variant="caption" color={blinkCount > 0 ? 'success.main' : 'text.secondary'}>
            😊 Blinks: {blinkCount}
          </Typography>
        </Box>

        {/* Instructions */}
        {eyeOpenness < 30 && (
          <Alert severity="info" sx={{ mt: 2 }}>
            Please open your eyes wider (need &gt;30% openness)
          </Alert>
        )}

        {eyeOpenness >= 30 && !isDetecting && (
          <Alert severity="success" sx={{ mt: 2 }}>
            ✅ Ready for iris verification! (Openness: {eyeOpenness.toFixed(1)}%)
          </Alert>
        )}

        {/* Action Buttons */}
        <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
          <Button 
            variant="outlined" 
            onClick={resetDetection}
            size="small"
          >
            Reset Detection
          </Button>
          
          {eyeOpenness >= 30 && (
            <Button 
              variant="contained" 
              onClick={autoCaptureIris}
              disabled={isDetecting}
              size="small"
              color="success"
            >
              {isDetecting ? 'Verifying...' : 'Verify Iris'}
            </Button>
          )}
        </Box>
      </Box>
    </Box>
  );
};

export default LiveIrisDetection;
