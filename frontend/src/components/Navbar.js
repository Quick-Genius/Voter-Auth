import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  IconButton,
  Menu,
  MenuItem,
} from '@mui/material';
import {
  HowToVote,
  Dashboard,
  Security,
  Menu as MenuIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

const Navbar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [anchorEl, setAnchorEl] = useState(null);

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleNavigation = (path) => {
    navigate(path);
    handleMenuClose();
  };

  const isActive = (path) => location.pathname === path;

  return (
    <AppBar 
      position="sticky" 
      sx={{ 
        background: 'linear-gradient(135deg, #1976d2 0%, #1565c0 100%)',
        boxShadow: '0 2px 20px rgba(0,0,0,0.1)',
      }}
    >
      <Toolbar>
        {/* Logo and Title */}
        <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
          <Security sx={{ mr: 2, fontSize: 32 }} />
          <Typography 
            variant="h6" 
            component="div" 
            sx={{ 
              fontWeight: 700,
              fontSize: { xs: '1rem', sm: '1.25rem' },
              cursor: 'pointer'
            }}
            onClick={() => navigate('/')}
          >
            Election Vote Auth
          </Typography>
        </Box>

        {/* Desktop Navigation */}
        <Box sx={{ display: { xs: 'none', md: 'flex' }, gap: 1 }}>
          <Button
            color="inherit"
            startIcon={<HowToVote />}
            onClick={() => handleNavigation('/')}
            sx={{
              fontWeight: isActive('/') ? 600 : 400,
              backgroundColor: isActive('/') ? 'rgba(255,255,255,0.1)' : 'transparent',
              '&:hover': {
                backgroundColor: 'rgba(255,255,255,0.1)',
              },
            }}
          >
            Home
          </Button>
          
          <Button
            color="inherit"
            startIcon={<Security />}
            onClick={() => handleNavigation('/booth-selection')}
            sx={{
              fontWeight: isActive('/booth-selection') ? 600 : 400,
              backgroundColor: isActive('/booth-selection') ? 'rgba(255,255,255,0.1)' : 'transparent',
              '&:hover': {
                backgroundColor: 'rgba(255,255,255,0.1)',
              },
            }}
          >
            Voter Verification
          </Button>
          
          <Button
            color="inherit"
            startIcon={<Dashboard />}
            onClick={() => handleNavigation('/dashboard')}
            sx={{
              fontWeight: isActive('/dashboard') ? 600 : 400,
              backgroundColor: isActive('/dashboard') ? 'rgba(255,255,255,0.1)' : 'transparent',
              '&:hover': {
                backgroundColor: 'rgba(255,255,255,0.1)',
              },
            }}
          >
            Dashboard
          </Button>
        </Box>

        {/* Mobile Navigation */}
        <Box sx={{ display: { xs: 'flex', md: 'none' } }}>
          <IconButton
            color="inherit"
            onClick={handleMenuOpen}
            sx={{ ml: 1 }}
          >
            <MenuIcon />
          </IconButton>
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
            PaperProps={{
              sx: {
                mt: 1,
                minWidth: 200,
                borderRadius: 2,
                boxShadow: '0 4px 20px rgba(0,0,0,0.15)',
              },
            }}
          >
            <MenuItem 
              onClick={() => handleNavigation('/')}
              sx={{ 
                py: 1.5,
                backgroundColor: isActive('/') ? 'rgba(25,118,210,0.1)' : 'transparent',
              }}
            >
              <HowToVote sx={{ mr: 2 }} />
              Home
            </MenuItem>
            <MenuItem 
              onClick={() => handleNavigation('/booth-selection')}
              sx={{ 
                py: 1.5,
                backgroundColor: isActive('/booth-selection') ? 'rgba(25,118,210,0.1)' : 'transparent',
              }}
            >
              <Security sx={{ mr: 2 }} />
              Voter Verification
            </MenuItem>
            <MenuItem 
              onClick={() => handleNavigation('/dashboard')}
              sx={{ 
                py: 1.5,
                backgroundColor: isActive('/dashboard') ? 'rgba(25,118,210,0.1)' : 'transparent',
              }}
            >
              <Dashboard sx={{ mr: 2 }} />
              Dashboard
            </MenuItem>
          </Menu>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
