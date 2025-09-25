import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  Button,
  CircularProgress,
  Alert,
  Chip,
  LinearProgress,
} from '@mui/material';
import {
  LocationOn,
  People,
  HowToVote,
  CheckCircle,
  ArrowForward,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-toastify';

const BoothSelection = () => {
  const navigate = useNavigate();
  const [booths, setBooths] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedBooth, setSelectedBooth] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchPollingBooths();
  }, []);

  const fetchPollingBooths = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:5001/api/polling-booths');
      setBooths(response.data);
      setError(null);
    } catch (error) {
      console.error('Error fetching polling booths:', error);
      setError('Failed to load polling booths. Please try again.');
      toast.error('Failed to load polling booths');
    } finally {
      setLoading(false);
    }
  };

  const handleBoothSelect = (booth) => {
    setSelectedBooth(booth);
  };

  const handleProceedToVerification = () => {
    if (selectedBooth) {
      navigate(`/verification/${selectedBooth.id}`);
    }
  };

  const getStatusColor = (turnout) => {
    if (turnout < 30) return '#4caf50'; // Green - Low turnout
    if (turnout < 70) return '#ff9800'; // Orange - Medium turnout
    return '#f44336'; // Red - High turnout
  };

  const getStatusText = (turnout) => {
    if (turnout < 30) return 'Low Traffic';
    if (turnout < 70) return 'Moderate Traffic';
    return 'High Traffic';
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
          <Box sx={{ textAlign: 'center' }}>
            <CircularProgress size={60} sx={{ mb: 2 }} />
            <Typography variant="h6" color="text.secondary">
              Loading Polling Booths...
            </Typography>
          </Box>
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert 
          severity="error" 
          sx={{ mb: 3 }}
          action={
            <Button color="inherit" size="small" onClick={fetchPollingBooths}>
              Retry
            </Button>
          }
        >
          {error}
        </Alert>
      </Container>
    );
  }

  return (
    <Box sx={{ minHeight: '100vh', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
      <Container maxWidth="lg" sx={{ py: 4 }}>
        {/* Header */}
        <Box sx={{ textAlign: 'center', mb: 4, color: 'white' }}>
          <Typography 
            variant="h2" 
            sx={{ 
              mb: 2, 
              fontWeight: 700,
              fontSize: { xs: '2rem', md: '2.5rem' },
            }}
            className="fade-in"
          >
            Select Polling Booth
          </Typography>
          <Typography 
            variant="h6" 
            sx={{ 
              opacity: 0.9,
              maxWidth: 600,
              mx: 'auto',
            }}
            className="fade-in"
          >
            Choose your assigned polling booth to begin the voter verification process
          </Typography>
        </Box>

        {/* Booth Selection Grid */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {booths.map((booth, index) => (
            <Grid item xs={12} md={4} key={booth.id}>
              <Card
                sx={{
                  height: '100%',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  background: selectedBooth?.id === booth.id 
                    ? 'linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%)'
                    : 'rgba(255,255,255,0.95)',
                  backdropFilter: 'blur(10px)',
                  border: selectedBooth?.id === booth.id 
                    ? '2px solid #1976d2' 
                    : '1px solid rgba(255,255,255,0.2)',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: '0 8px 25px rgba(0,0,0,0.15)',
                    border: '2px solid #1976d2',
                  },
                }}
                onClick={() => handleBoothSelect(booth)}
                className={`booth-card ${selectedBooth?.id === booth.id ? 'selected' : ''} slide-in`}
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <CardContent sx={{ p: 3 }}>
                  {/* Booth Header */}
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h5" sx={{ fontWeight: 600, color: '#1976d2' }}>
                      Booth {booth.booth_number}
                    </Typography>
                    {selectedBooth?.id === booth.id && (
                      <CheckCircle sx={{ color: '#4caf50', fontSize: 28 }} />
                    )}
                  </Box>

                  {/* Location */}
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <LocationOn sx={{ mr: 1, color: 'text.secondary' }} />
                    <Typography variant="body2" color="text.secondary">
                      {booth.location}
                    </Typography>
                  </Box>

                  {/* Statistics */}
                  <Box sx={{ mb: 3 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2" color="text.secondary">
                        Voter Turnout
                      </Typography>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        {booth.votes_cast} / {booth.total_voters}
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={booth.turnout_percentage}
                      sx={{
                        height: 8,
                        borderRadius: 4,
                        backgroundColor: 'rgba(0,0,0,0.1)',
                        '& .MuiLinearProgress-bar': {
                          backgroundColor: getStatusColor(booth.turnout_percentage),
                          borderRadius: 4,
                        },
                      }}
                    />
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
                      <Typography variant="caption" color="text.secondary">
                        {booth.turnout_percentage}% turnout
                      </Typography>
                      <Chip
                        label={getStatusText(booth.turnout_percentage)}
                        size="small"
                        sx={{
                          backgroundColor: getStatusColor(booth.turnout_percentage),
                          color: 'white',
                          fontSize: '0.7rem',
                          height: 20,
                        }}
                      />
                    </Box>
                  </Box>

                  {/* Capacity Info */}
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <People sx={{ mr: 1, color: 'text.secondary', fontSize: 20 }} />
                      <Typography variant="body2" color="text.secondary">
                        Capacity: {booth.capacity}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <HowToVote sx={{ mr: 1, color: 'text.secondary', fontSize: 20 }} />
                      <Typography variant="body2" color="text.secondary">
                        {booth.total_voters} voters
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        {/* Selected Booth Info */}
        {selectedBooth && (
          <Card
            sx={{
              mb: 4,
              background: 'rgba(255,255,255,0.95)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255,255,255,0.2)',
            }}
            className="fade-in"
          >
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600, color: '#1976d2' }}>
                Selected Polling Booth Details
              </Typography>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Booth Number
                    </Typography>
                    <Typography variant="body1" sx={{ fontWeight: 500 }}>
                      {selectedBooth.booth_number}
                    </Typography>
                  </Box>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Location
                    </Typography>
                    <Typography variant="body1" sx={{ fontWeight: 500 }}>
                      {selectedBooth.location}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Total Registered Voters
                    </Typography>
                    <Typography variant="body1" sx={{ fontWeight: 500 }}>
                      {selectedBooth.total_voters}
                    </Typography>
                  </Box>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Votes Cast Today
                    </Typography>
                    <Typography variant="body1" sx={{ fontWeight: 500 }}>
                      {selectedBooth.votes_cast} ({selectedBooth.turnout_percentage}%)
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        )}

        {/* Proceed Button */}
        {selectedBooth && (
          <Box sx={{ textAlign: 'center' }}>
            <Button
              variant="contained"
              size="large"
              onClick={handleProceedToVerification}
              endIcon={<ArrowForward />}
              sx={{
                px: 4,
                py: 1.5,
                fontSize: '1.1rem',
                fontWeight: 600,
                background: 'linear-gradient(135deg, #1976d2 0%, #1565c0 100%)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #1565c0 0%, #0d47a1 100%)',
                  transform: 'translateY(-2px)',
                },
                transition: 'all 0.3s ease',
              }}
              className="pulse"
            >
              Proceed to Voter Verification
            </Button>
          </Box>
        )}

        {/* Instructions */}
        <Card
          sx={{
            mt: 4,
            background: 'rgba(255,255,255,0.95)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255,255,255,0.2)',
          }}
        >
          <CardContent sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 600, color: '#1976d2' }}>
              Instructions
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <Typography variant="body2" color="text.secondary">
                • Select the polling booth where you are registered to vote
              </Typography>
              <Typography variant="body2" color="text.secondary">
                • Ensure you have your voter ID card ready for verification
              </Typography>
              <Typography variant="body2" color="text.secondary">
                • The verification process includes ID scanning, face recognition, and iris detection
              </Typography>
              <Typography variant="body2" color="text.secondary">
                • After successful verification, you will be directed to the EVM for voting
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Container>
    </Box>
  );
};

export default BoothSelection;
