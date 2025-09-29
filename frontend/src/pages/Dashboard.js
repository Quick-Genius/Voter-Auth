import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  LinearProgress,
  Alert,
  Button,
  CircularProgress,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  People,
  HowToVote,
  Security,
  Warning,
  Refresh,
  TrendingUp,
  LocationOn,
  AccessTime,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
} from 'recharts';
import axios from 'axios';
import { toast } from 'react-toastify';
import { format } from 'date-fns';

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [fraudAttempts, setFraudAttempts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  useEffect(() => {
    fetchDashboardData();
    fetchFraudAttempts();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(() => {
      fetchDashboardData();
      fetchFraudAttempts();
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await axios.get('http://localhost:5001/api/dashboard/stats');
      setDashboardData(response.data);
      setLastUpdated(new Date());
      setError(null);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setError('Failed to load dashboard data');
      toast.error('Failed to load dashboard data');
    }
  };

  const fetchFraudAttempts = async () => {
    try {
      const response = await axios.get('http://localhost:5001/api/fraud-attempts');
      setFraudAttempts(response.data);
    } catch (error) {
      console.error('Error fetching fraud attempts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    setLoading(true);
    fetchDashboardData();
    fetchFraudAttempts();
  };

  const getStatusColor = (turnout) => {
    if (turnout < 30) return '#4caf50';
    if (turnout < 70) return '#ff9800';
    return '#f44336';
  };

  const getStatusText = (turnout) => {
    if (turnout < 30) return 'Low';
    if (turnout < 70) return 'Moderate';
    return 'High';
  };

  const getFraudTypeColor = (type) => {
    switch (type) {
      case 'duplicate_vote': return '#f44336';
      case 'identity_mismatch': return '#ff9800';
      default: return '#9e9e9e';
    }
  };

  // Chart data preparation
  const pieChartData = dashboardData?.booth_stats?.map(booth => ({
    name: `Booth ${booth.booth_number}`,
    value: booth.votes_cast,
    color: getStatusColor(booth.turnout_percentage),
  })) || [];

  const barChartData = dashboardData?.booth_stats?.map(booth => ({
    booth: booth.booth_number,
    votes: booth.votes_cast,
    total: booth.total_voters,
    turnout: booth.turnout_percentage,
  })) || [];

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  if (loading && !dashboardData) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
          <Box sx={{ textAlign: 'center' }}>
            <CircularProgress size={60} sx={{ mb: 2 }} />
            <Typography variant="h6" color="text.secondary">
              Loading Dashboard...
            </Typography>
          </Box>
        </Box>
      </Container>
    );
  }

  return (
    <Box sx={{ minHeight: '100vh', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
      <Container maxWidth="lg" sx={{ py: 4 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
          <Box sx={{ color: 'white' }}>
            <Typography 
              variant="h3" 
              sx={{ 
                mb: 1, 
                fontWeight: 700,
                fontSize: { xs: '1.8rem', md: '2.5rem' },
              }}
            >
              Election Commission Dashboard
            </Typography>
            <Typography variant="h6" sx={{ opacity: 0.9 }}>
              Real-time monitoring and analytics
            </Typography>
            {lastUpdated && (
              <Typography variant="body2" sx={{ opacity: 0.7, mt: 1 }}>
                Last updated: {format(lastUpdated, 'HH:mm:ss')}
              </Typography>
            )}
          </Box>
          <Tooltip title="Refresh Data">
            <IconButton
              onClick={handleRefresh}
              sx={{
                bgcolor: 'rgba(255,255,255,0.2)',
                color: 'white',
                '&:hover': {
                  bgcolor: 'rgba(255,255,255,0.3)',
                },
              }}
            >
              <Refresh />
            </IconButton>
          </Tooltip>
        </Box>

        {error && (
          <Alert 
            severity="error" 
            sx={{ mb: 3 }}
            action={
              <Button color="inherit" size="small" onClick={handleRefresh}>
                Retry
              </Button>
            }
          >
            {error}
          </Alert>
        )}

        {dashboardData && (
          <>
            {/* Overview Cards */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
              <Grid item xs={12} sm={6} md={3}>
                <Card sx={{ background: 'rgba(255,255,255,0.95)', backdropFilter: 'blur(10px)' }}>
                  <CardContent sx={{ textAlign: 'center', p: 3 }}>
                    <Box
                      sx={{
                        p: 2,
                        borderRadius: '50%',
                        bgcolor: '#e3f2fd',
                        color: '#1976d2',
                        display: 'inline-flex',
                        mb: 2,
                      }}
                    >
                      <LocationOn sx={{ fontSize: 32 }} />
                    </Box>
                    <Typography variant="h4" sx={{ fontWeight: 700, color: '#1976d2', mb: 1 }}>
                      {dashboardData.overall.total_booths}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Polling Booths
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <Card sx={{ background: 'rgba(255,255,255,0.95)', backdropFilter: 'blur(10px)' }}>
                  <CardContent sx={{ textAlign: 'center', p: 3 }}>
                    <Box
                      sx={{
                        p: 2,
                        borderRadius: '50%',
                        bgcolor: '#e8f5e8',
                        color: '#2e7d32',
                        display: 'inline-flex',
                        mb: 2,
                      }}
                    >
                      <People sx={{ fontSize: 32 }} />
                    </Box>
                    <Typography variant="h4" sx={{ fontWeight: 700, color: '#2e7d32', mb: 1 }}>
                      {dashboardData.overall.total_voters.toLocaleString()}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Registered Voters
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <Card sx={{ background: 'rgba(255,255,255,0.95)', backdropFilter: 'blur(10px)' }}>
                  <CardContent sx={{ textAlign: 'center', p: 3 }}>
                    <Box
                      sx={{
                        p: 2,
                        borderRadius: '50%',
                        bgcolor: '#fff3e0',
                        color: '#ed6c02',
                        display: 'inline-flex',
                        mb: 2,
                      }}
                    >
                      <HowToVote sx={{ fontSize: 32 }} />
                    </Box>
                    <Typography variant="h4" sx={{ fontWeight: 700, color: '#ed6c02', mb: 1 }}>
                      {dashboardData.overall.total_votes_cast.toLocaleString()}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Votes Cast
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <Card sx={{ background: 'rgba(255,255,255,0.95)', backdropFilter: 'blur(10px)' }}>
                  <CardContent sx={{ textAlign: 'center', p: 3 }}>
                    <Box
                      sx={{
                        p: 2,
                        borderRadius: '50%',
                        bgcolor: '#fce4ec',
                        color: '#d32f2f',
                        display: 'inline-flex',
                        mb: 2,
                      }}
                    >
                      <Warning sx={{ fontSize: 32 }} />
                    </Box>
                    <Typography variant="h4" sx={{ fontWeight: 700, color: '#d32f2f', mb: 1 }}>
                      {dashboardData.overall.fraud_attempts}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Fraud Attempts
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            {/* Overall Turnout */}
            <Card sx={{ mb: 4, background: 'rgba(255,255,255,0.95)', backdropFilter: 'blur(10px)' }}>
              <CardContent sx={{ p: 3 }}>
                <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                  Overall Voter Turnout
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h4" sx={{ fontWeight: 700, color: '#1976d2', mr: 2 }}>
                    {dashboardData.overall.overall_turnout}%
                  </Typography>
                  <TrendingUp sx={{ color: '#4caf50' }} />
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={dashboardData.overall.overall_turnout}
                  sx={{
                    height: 12,
                    borderRadius: 6,
                    backgroundColor: 'rgba(0,0,0,0.1)',
                    '& .MuiLinearProgress-bar': {
                      backgroundColor: '#1976d2',
                      borderRadius: 6,
                    },
                  }}
                />
              </CardContent>
            </Card>

            {/* Charts Section */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
              <Grid item xs={12} md={6}>
                <Card sx={{ background: 'rgba(255,255,255,0.95)', backdropFilter: 'blur(10px)' }}>
                  <CardContent sx={{ p: 3 }}>
                    <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
                      Votes by Polling Booth
                    </Typography>
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie
                          data={pieChartData}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={({ name, value }) => `${name}: ${value}`}
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="value"
                        >
                          {pieChartData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <RechartsTooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} md={6}>
                <Card sx={{ background: 'rgba(255,255,255,0.95)', backdropFilter: 'blur(10px)' }}>
                  <CardContent sx={{ p: 3 }}>
                    <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
                      Turnout by Booth
                    </Typography>
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={barChartData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="booth" />
                        <YAxis />
                        <RechartsTooltip />
                        <Bar dataKey="turnout" fill="#1976d2" />
                      </BarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            {/* Booth Details Table */}
            <Card sx={{ mb: 4, background: 'rgba(255,255,255,0.95)', backdropFilter: 'blur(10px)' }}>
              <CardContent sx={{ p: 3 }}>
                <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
                  Polling Booth Details
                </Typography>
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell sx={{ fontWeight: 600 }}>Booth</TableCell>
                        <TableCell sx={{ fontWeight: 600 }}>Location</TableCell>
                        <TableCell sx={{ fontWeight: 600 }}>Voters</TableCell>
                        <TableCell sx={{ fontWeight: 600 }}>Votes Cast</TableCell>
                        <TableCell sx={{ fontWeight: 600 }}>Turnout</TableCell>
                        <TableCell sx={{ fontWeight: 600 }}>Status</TableCell>
                        <TableCell sx={{ fontWeight: 600 }}>Recent Activity</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {dashboardData.booth_stats.map((booth) => (
                        <TableRow key={booth.booth_number}>
                          <TableCell sx={{ fontWeight: 600 }}>
                            {booth.booth_number}
                          </TableCell>
                          <TableCell>{booth.location}</TableCell>
                          <TableCell>{booth.total_voters}</TableCell>
                          <TableCell>{booth.votes_cast}</TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <LinearProgress
                                variant="determinate"
                                value={booth.turnout_percentage}
                                sx={{
                                  width: 60,
                                  height: 6,
                                  borderRadius: 3,
                                  backgroundColor: 'rgba(0,0,0,0.1)',
                                  '& .MuiLinearProgress-bar': {
                                    backgroundColor: getStatusColor(booth.turnout_percentage),
                                    borderRadius: 3,
                                  },
                                }}
                              />
                              <Typography variant="body2" sx={{ minWidth: 40 }}>
                                {booth.turnout_percentage}%
                              </Typography>
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={getStatusText(booth.turnout_percentage)}
                              size="small"
                              sx={{
                                backgroundColor: getStatusColor(booth.turnout_percentage),
                                color: 'white',
                                fontWeight: 500,
                              }}
                            />
                          </TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <AccessTime sx={{ fontSize: 16, color: 'text.secondary' }} />
                              <Typography variant="body2" color="text.secondary">
                                {booth.recent_votes_1h} votes (1h)
                              </Typography>
                            </Box>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>

            {/* Fraud Attempts */}
            {fraudAttempts.length > 0 && (
              <Card sx={{ background: 'rgba(255,255,255,0.95)', backdropFilter: 'blur(10px)' }}>
                <CardContent sx={{ p: 3 }}>
                  <Typography variant="h6" sx={{ mb: 3, fontWeight: 600, color: '#d32f2f' }}>
                    Recent Fraud Attempts
                  </Typography>
                  <TableContainer>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell sx={{ fontWeight: 600 }}>Time</TableCell>
                          <TableCell sx={{ fontWeight: 600 }}>Voter ID</TableCell>
                          <TableCell sx={{ fontWeight: 600 }}>Booth</TableCell>
                          <TableCell sx={{ fontWeight: 600 }}>Type</TableCell>
                          <TableCell sx={{ fontWeight: 600 }}>Details</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {fraudAttempts.slice(0, 10).map((attempt) => (
                          <TableRow key={attempt.id}>
                            <TableCell>
                              {format(new Date(attempt.timestamp), 'MMM dd, HH:mm')}
                            </TableCell>
                            <TableCell sx={{ fontWeight: 600 }}>
                              {attempt.voter_id}
                            </TableCell>
                            <TableCell>{attempt.booth_number}</TableCell>
                            <TableCell>
                              <Chip
                                label={attempt.fraud_type.replace('_', ' ')}
                                size="small"
                                sx={{
                                  backgroundColor: getFraudTypeColor(attempt.fraud_type),
                                  color: 'white',
                                  fontWeight: 500,
                                }}
                              />
                            </TableCell>
                            <TableCell>
                              <Typography variant="body2" color="text.secondary">
                                {attempt.details}
                              </Typography>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </CardContent>
              </Card>
            )}
          </>
        )}
      </Container>
    </Box>
  );
};

export default Dashboard;
