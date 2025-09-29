import React from 'react';
import {
  Container,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  Button,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
} from '@mui/material';
import {
  Security,
  Fingerprint,
  RemoveRedEye,
  CreditCard,
  Dashboard,
  Block,
  CheckCircle,
  Speed,
  Lock,
  Visibility,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const HomePage = () => {
  const navigate = useNavigate();

  const features = [
    {
      icon: <CreditCard />,
      title: 'OCR Voter ID Verification',
      description: 'Automated scanning and verification of voter ID cards using advanced OCR technology',
      color: '#1976d2',
    },
    {
      icon: <Fingerprint />,
      title: 'Face Recognition',
      description: 'Biometric face matching with stored voter database for identity verification',
      color: '#2e7d32',
    },
    {
      icon: <RemoveRedEye />,
      title: 'Iris Detection',
      description: 'Advanced iris recognition for enhanced security and fraud prevention',
      color: '#ed6c02',
    },
    {
      icon: <Security />,
      title: 'Blockchain Integration',
      description: 'Immutable vote recording and audit trail using blockchain technology',
      color: '#9c27b0',
    },
  ];

  const benefits = [
    { icon: <Block />, text: 'Prevents duplicate voting across polling booths' },
    { icon: <CheckCircle />, text: 'Ensures authentic voter identity verification' },
    { icon: <Speed />, text: 'Real-time fraud detection and prevention' },
    { icon: <Dashboard />, text: 'Live polling booth monitoring and statistics' },
    { icon: <Lock />, text: 'Secure biometric data protection' },
    { icon: <Visibility />, text: 'Transparent and auditable voting process' },
  ];

  const stats = [
    { label: 'Security Layers', value: '3+', color: '#1976d2' },
    { label: 'Fraud Prevention', value: '99.9%', color: '#2e7d32' },
    { label: 'Verification Speed', value: '<30s', color: '#ed6c02' },
    { label: 'Accuracy Rate', value: '99.8%', color: '#9c27b0' },
  ];

  return (
    <Box sx={{ minHeight: '100vh', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
      <Container maxWidth="lg" sx={{ py: 4 }}>
        {/* Hero Section */}
        <Box sx={{ textAlign: 'center', mb: 6, color: 'white' }}>
          <Typography 
            variant="h1" 
            sx={{ 
              mb: 2, 
              fontSize: { xs: '2rem', md: '3rem' },
              fontWeight: 700,
              textShadow: '0 2px 4px rgba(0,0,0,0.3)',
            }}
            className="fade-in"
          >
            Election Vote Authentication System
          </Typography>
          <Typography 
            variant="h5" 
            sx={{ 
              mb: 4, 
              opacity: 0.9,
              fontSize: { xs: '1.1rem', md: '1.5rem' },
              maxWidth: 800,
              mx: 'auto',
            }}
            className="fade-in"
          >
            Securing democratic processes through advanced biometric verification and blockchain technology
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Button
              variant="contained"
              size="large"
              onClick={() => navigate('/booth-selection')}
              sx={{
                bgcolor: 'white',
                color: '#1976d2',
                px: 4,
                py: 1.5,
                fontSize: '1.1rem',
                fontWeight: 600,
                '&:hover': {
                  bgcolor: '#f5f5f5',
                  transform: 'translateY(-2px)',
                },
                transition: 'all 0.3s ease',
              }}
              className="pulse"
            >
              Start Voter Verification
            </Button>
            <Button
              variant="outlined"
              size="large"
              onClick={() => navigate('/dashboard')}
              sx={{
                borderColor: 'white',
                color: 'white',
                px: 4,
                py: 1.5,
                fontSize: '1.1rem',
                fontWeight: 600,
                '&:hover': {
                  borderColor: 'white',
                  bgcolor: 'rgba(255,255,255,0.1)',
                  transform: 'translateY(-2px)',
                },
                transition: 'all 0.3s ease',
              }}
            >
              View Dashboard
            </Button>
          </Box>
        </Box>

        {/* Statistics Section */}
        <Grid container spacing={3} sx={{ mb: 6 }}>
          {stats.map((stat, index) => (
            <Grid item xs={6} md={3} key={index}>
              <Paper
                sx={{
                  p: 3,
                  textAlign: 'center',
                  background: 'rgba(255,255,255,0.95)',
                  backdropFilter: 'blur(10px)',
                  border: '1px solid rgba(255,255,255,0.2)',
                }}
                className="fade-in dashboard-card"
              >
                <Typography 
                  variant="h3" 
                  sx={{ 
                    color: stat.color, 
                    fontWeight: 700,
                    mb: 1,
                  }}
                >
                  {stat.value}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {stat.label}
                </Typography>
              </Paper>
            </Grid>
          ))}
        </Grid>

        {/* Features Section */}
        <Box sx={{ mb: 6 }}>
          <Typography 
            variant="h2" 
            sx={{ 
              textAlign: 'center', 
              mb: 4, 
              color: 'white',
              fontWeight: 600,
            }}
          >
            Advanced Security Features
          </Typography>
          <Grid container spacing={3}>
            {features.map((feature, index) => (
              <Grid item xs={12} md={6} key={index}>
                <Card
                  sx={{
                    height: '100%',
                    background: 'rgba(255,255,255,0.95)',
                    backdropFilter: 'blur(10px)',
                    border: '1px solid rgba(255,255,255,0.2)',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: '0 8px 25px rgba(0,0,0,0.15)',
                    },
                  }}
                  className="slide-in"
                >
                  <CardContent sx={{ p: 3 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Box
                        sx={{
                          p: 1.5,
                          borderRadius: 2,
                          bgcolor: feature.color,
                          color: 'white',
                          mr: 2,
                        }}
                      >
                        {feature.icon}
                      </Box>
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        {feature.title}
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      {feature.description}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>

        {/* Benefits Section */}
        <Grid container spacing={4} sx={{ mb: 6 }}>
          <Grid item xs={12} md={6}>
            <Paper
              sx={{
                p: 4,
                background: 'rgba(255,255,255,0.95)',
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(255,255,255,0.2)',
                height: '100%',
              }}
            >
              <Typography 
                variant="h4" 
                sx={{ 
                  mb: 3, 
                  fontWeight: 600,
                  color: '#1976d2',
                }}
              >
                Key Benefits
              </Typography>
              <List>
                {benefits.map((benefit, index) => (
                  <ListItem key={index} sx={{ px: 0 }}>
                    <ListItemIcon>
                      <Box
                        sx={{
                          p: 1,
                          borderRadius: '50%',
                          bgcolor: '#e3f2fd',
                          color: '#1976d2',
                        }}
                      >
                        {benefit.icon}
                      </Box>
                    </ListItemIcon>
                    <ListItemText 
                      primary={benefit.text}
                      sx={{
                        '& .MuiListItemText-primary': {
                          fontWeight: 500,
                        },
                      }}
                    />
                  </ListItem>
                ))}
              </List>
            </Paper>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Paper
              sx={{
                p: 4,
                background: 'rgba(255,255,255,0.95)',
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(255,255,255,0.2)',
                height: '100%',
              }}
            >
              <Typography 
                variant="h4" 
                sx={{ 
                  mb: 3, 
                  fontWeight: 600,
                  color: '#1976d2',
                }}
              >
                How It Works
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Chip 
                    label="1" 
                    sx={{ 
                      bgcolor: '#1976d2', 
                      color: 'white',
                      fontWeight: 600,
                      minWidth: 32,
                    }} 
                  />
                  <Typography>Voter presents ID card for OCR verification</Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Chip 
                    label="2" 
                    sx={{ 
                      bgcolor: '#2e7d32', 
                      color: 'white',
                      fontWeight: 600,
                      minWidth: 32,
                    }} 
                  />
                  <Typography>Face recognition matches with database</Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Chip 
                    label="3" 
                    sx={{ 
                      bgcolor: '#ed6c02', 
                      color: 'white',
                      fontWeight: 600,
                      minWidth: 32,
                    }} 
                  />
                  <Typography>Iris detection for enhanced security</Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Chip 
                    label="4" 
                    sx={{ 
                      bgcolor: '#9c27b0', 
                      color: 'white',
                      fontWeight: 600,
                      minWidth: 32,
                    }} 
                  />
                  <Typography>Voter authenticated and can proceed to EVM</Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Chip 
                    label="5" 
                    sx={{ 
                      bgcolor: '#d32f2f', 
                      color: 'white',
                      fontWeight: 600,
                      minWidth: 32,
                    }} 
                  />
                  <Typography>Vote recorded on blockchain for audit trail</Typography>
                </Box>
              </Box>
            </Paper>
          </Grid>
        </Grid>

        {/* Call to Action */}
        <Paper
          sx={{
            p: 4,
            textAlign: 'center',
            background: 'rgba(255,255,255,0.95)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255,255,255,0.2)',
          }}
        >
          <Typography 
            variant="h4" 
            sx={{ 
              mb: 2, 
              fontWeight: 600,
              color: '#1976d2',
            }}
          >
            Ready to Experience Secure Voting?
          </Typography>
          <Typography 
            variant="body1" 
            sx={{ 
              mb: 3,
              color: 'text.secondary',
              maxWidth: 600,
              mx: 'auto',
            }}
          >
            Join the future of election security with our comprehensive voter authentication system. 
            Ensure every vote counts and every voter is verified.
          </Typography>
          <Button
            variant="contained"
            size="large"
            onClick={() => navigate('/booth-selection')}
            sx={{
              px: 4,
              py: 1.5,
              fontSize: '1.1rem',
              fontWeight: 600,
            }}
          >
            Get Started Now
          </Button>
        </Paper>
      </Container>
    </Box>
  );
};

export default HomePage;
