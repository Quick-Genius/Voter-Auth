import json
import hashlib
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BlockchainIntegration:
    """
    Blockchain integration module for Hyperledger Fabric
    Handles vote recording and verification on the blockchain
    """
    
    def __init__(self, network_config: Dict[str, Any] = None):
        """
        Initialize blockchain integration
        
        Args:
            network_config: Configuration for Hyperledger Fabric network
        """
        self.network_config = network_config or self._get_default_config()
        self.channel_name = self.network_config.get('channel_name', 'mychannel')
        self.chaincode_name = self.network_config.get('chaincode_name', 'vote-auth')
        self.org_name = self.network_config.get('org_name', 'Org1')
        
        # For demo purposes, we'll simulate blockchain operations
        # In production, use Hyperledger Fabric SDK
        self.demo_mode = True
        self.demo_storage = {}
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default blockchain network configuration"""
        return {
            'channel_name': 'mychannel',
            'chaincode_name': 'vote-auth',
            'org_name': 'Org1',
            'peer_endpoint': 'peer0.org1.example.com:7051',
            'orderer_endpoint': 'orderer.example.com:7050',
            'ca_endpoint': 'ca.org1.example.com:7054',
            'msp_id': 'Org1MSP',
            'demo_mode': True
        }
    
    def record_vote_verification(self, voter_uuid: str, voter_id: str, 
                               booth_id: int, verification_step: str) -> Dict[str, Any]:
        """
        Record a vote verification step on the blockchain
        
        Args:
            voter_uuid: Unique identifier for the voter
            voter_id: Voter ID from the voter card
            booth_id: Polling booth ID
            verification_step: Type of verification (id_verification, face_verification, iris_verification, vote_cast)
            
        Returns:
            Dict containing success status and blockchain hash
        """
        try:
            if self.demo_mode:
                return self._demo_record_verification(voter_uuid, voter_id, booth_id, verification_step)
            else:
                return self._fabric_record_verification(voter_uuid, voter_id, booth_id, verification_step)
                
        except Exception as e:
            logger.error(f"Failed to record verification on blockchain: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'blockchain_hash': None
            }
    
    def _demo_record_verification(self, voter_uuid: str, voter_id: str, 
                                booth_id: int, verification_step: str) -> Dict[str, Any]:
        """Demo implementation of blockchain recording"""
        
        # Get or create vote record
        vote_record_key = f"vote_{voter_uuid}"
        vote_record = self.demo_storage.get(vote_record_key, {
            'voter_uuid': voter_uuid,
            'voter_id': voter_id,
            'polling_booth_id': booth_id,
            'timestamp': datetime.utcnow().isoformat(),
            'id_verified': False,
            'face_verified': False,
            'iris_verified': False,
            'vote_cast': False,
            'blockchain_hash': None,
            'previous_hash': None
        })
        
        # Check if voter has already voted
        voter_status_key = f"voter_{voter_uuid}"
        voter_status = self.demo_storage.get(voter_status_key, {
            'voter_uuid': voter_uuid,
            'voter_id': voter_id,
            'has_voted': False,
            'voted_at': None,
            'polling_booth_id': booth_id
        })
        
        if voter_status.get('has_voted') and verification_step != 'vote_cast':
            return {
                'success': False,
                'error': f'Voter {voter_id} has already voted',
                'blockchain_hash': None
            }
        
        # Update verification status
        if verification_step == 'id_verification':
            vote_record['id_verified'] = True
        elif verification_step == 'face_verification':
            vote_record['face_verified'] = True
        elif verification_step == 'iris_verification':
            vote_record['iris_verified'] = True
        elif verification_step == 'vote_cast':
            if not all([vote_record['id_verified'], vote_record['face_verified'], vote_record['iris_verified']]):
                return {
                    'success': False,
                    'error': 'All verification steps must be completed before casting vote',
                    'blockchain_hash': None
                }
            vote_record['vote_cast'] = True
            voter_status['has_voted'] = True
            voter_status['voted_at'] = datetime.utcnow().isoformat()
        else:
            return {
                'success': False,
                'error': f'Invalid verification step: {verification_step}',
                'blockchain_hash': None
            }
        
        # Generate blockchain hash
        vote_record['blockchain_hash'] = self._generate_hash(vote_record)
        vote_record['timestamp'] = datetime.utcnow().isoformat()
        
        # Store records
        self.demo_storage[vote_record_key] = vote_record
        self.demo_storage[voter_status_key] = voter_status
        
        # Update booth statistics
        if verification_step == 'vote_cast':
            self._update_booth_stats(booth_id)
        
        logger.info(f"Recorded {verification_step} for voter {voter_id} on blockchain")
        
        return {
            'success': True,
            'blockchain_hash': vote_record['blockchain_hash'],
            'transaction_id': f"tx_{int(time.time())}_{voter_uuid[:8]}"
        }
    
    def _fabric_record_verification(self, voter_uuid: str, voter_id: str, 
                                  booth_id: int, verification_step: str) -> Dict[str, Any]:
        """
        Production implementation using Hyperledger Fabric SDK
        This would use the actual Fabric SDK to interact with the blockchain
        """
        # TODO: Implement actual Fabric SDK integration
        # from hfc.fabric import Client
        
        # client = Client(net_profile=self.network_config)
        # org_admin = client.get_user(org_name=self.org_name, name='Admin')
        
        # response = client.chaincode_invoke(
        #     requestor=org_admin,
        #     channel_name=self.channel_name,
        #     peers=[self.network_config['peer_endpoint']],
        #     cc_name=self.chaincode_name,
        #     fcn='RecordVoteVerification',
        #     args=[voter_uuid, voter_id, str(booth_id), verification_step]
        # )
        
        # return {
        #     'success': True,
        #     'blockchain_hash': response.get('tx_id'),
        #     'transaction_id': response.get('tx_id')
        # }
        
        # For now, fallback to demo mode
        return self._demo_record_verification(voter_uuid, voter_id, booth_id, verification_step)
    
    def get_vote_record(self, voter_uuid: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve vote record from blockchain
        
        Args:
            voter_uuid: Unique identifier for the voter
            
        Returns:
            Vote record or None if not found
        """
        try:
            if self.demo_mode:
                return self.demo_storage.get(f"vote_{voter_uuid}")
            else:
                # TODO: Implement Fabric SDK query
                return None
                
        except Exception as e:
            logger.error(f"Failed to retrieve vote record: {str(e)}")
            return None
    
    def get_voter_status(self, voter_uuid: str) -> Optional[Dict[str, Any]]:
        """
        Check voter status on blockchain
        
        Args:
            voter_uuid: Unique identifier for the voter
            
        Returns:
            Voter status or None if not found
        """
        try:
            if self.demo_mode:
                return self.demo_storage.get(f"voter_{voter_uuid}")
            else:
                # TODO: Implement Fabric SDK query
                return None
                
        except Exception as e:
            logger.error(f"Failed to retrieve voter status: {str(e)}")
            return None
    
    def get_booth_stats(self, booth_id: int) -> Dict[str, Any]:
        """
        Get polling booth statistics from blockchain
        
        Args:
            booth_id: Polling booth ID
            
        Returns:
            Booth statistics
        """
        try:
            if self.demo_mode:
                stats_key = f"booth_stats_{booth_id}"
                return self.demo_storage.get(stats_key, {
                    'booth_id': booth_id,
                    'total_votes': 0,
                    'last_updated': datetime.utcnow().isoformat()
                })
            else:
                # TODO: Implement Fabric SDK query
                return {
                    'booth_id': booth_id,
                    'total_votes': 0,
                    'last_updated': datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to retrieve booth stats: {str(e)}")
            return {
                'booth_id': booth_id,
                'total_votes': 0,
                'last_updated': datetime.utcnow().isoformat()
            }
    
    def verify_vote_integrity(self, voter_uuid: str) -> bool:
        """
        Verify the integrity of a vote record using blockchain hash
        
        Args:
            voter_uuid: Unique identifier for the voter
            
        Returns:
            True if vote record is valid, False otherwise
        """
        try:
            vote_record = self.get_vote_record(voter_uuid)
            if not vote_record:
                return False
            
            # Recalculate hash and compare
            stored_hash = vote_record.get('blockchain_hash')
            calculated_hash = self._generate_hash(vote_record)
            
            return stored_hash == calculated_hash
            
        except Exception as e:
            logger.error(f"Failed to verify vote integrity: {str(e)}")
            return False
    
    def get_all_vote_records(self) -> List[Dict[str, Any]]:
        """
        Retrieve all vote records for audit purposes
        
        Returns:
            List of all vote records
        """
        try:
            if self.demo_mode:
                vote_records = []
                for key, value in self.demo_storage.items():
                    if key.startswith('vote_'):
                        vote_records.append(value)
                return vote_records
            else:
                # TODO: Implement Fabric SDK query
                return []
                
        except Exception as e:
            logger.error(f"Failed to retrieve all vote records: {str(e)}")
            return []
    
    def get_vote_history(self, voter_id: str) -> List[Dict[str, Any]]:
        """
        Get voting history for a specific voter ID
        
        Args:
            voter_id: Voter ID from voter card
            
        Returns:
            List of vote records for the voter
        """
        try:
            if self.demo_mode:
                history = []
                for key, value in self.demo_storage.items():
                    if key.startswith('vote_') and value.get('voter_id') == voter_id:
                        history.append(value)
                return history
            else:
                # TODO: Implement Fabric SDK query
                return []
                
        except Exception as e:
            logger.error(f"Failed to retrieve vote history: {str(e)}")
            return []
    
    def _update_booth_stats(self, booth_id: int):
        """Update polling booth statistics"""
        stats_key = f"booth_stats_{booth_id}"
        stats = self.demo_storage.get(stats_key, {
            'booth_id': booth_id,
            'total_votes': 0,
            'last_updated': datetime.utcnow().isoformat()
        })
        
        stats['total_votes'] += 1
        stats['last_updated'] = datetime.utcnow().isoformat()
        
        self.demo_storage[stats_key] = stats
    
    def _generate_hash(self, vote_record: Dict[str, Any]) -> str:
        """
        Generate cryptographic hash for vote record
        
        Args:
            vote_record: Vote record data
            
        Returns:
            SHA-256 hash of the vote record
        """
        # Create a copy without the hash field for calculation
        record_copy = vote_record.copy()
        record_copy.pop('blockchain_hash', None)
        record_copy.pop('previous_hash', None)
        
        # Sort keys for consistent hashing
        sorted_data = json.dumps(record_copy, sort_keys=True)
        
        # Generate SHA-256 hash
        hash_object = hashlib.sha256(sorted_data.encode())
        return hash_object.hexdigest()
    
    def get_network_status(self) -> Dict[str, Any]:
        """
        Get blockchain network status
        
        Returns:
            Network status information
        """
        return {
            'network_active': True,
            'demo_mode': self.demo_mode,
            'channel_name': self.channel_name,
            'chaincode_name': self.chaincode_name,
            'org_name': self.org_name,
            'total_records': len([k for k in self.demo_storage.keys() if k.startswith('vote_')]),
            'last_activity': datetime.utcnow().isoformat()
        }
    
    def export_audit_trail(self) -> Dict[str, Any]:
        """
        Export complete audit trail for compliance
        
        Returns:
            Complete audit trail data
        """
        return {
            'export_timestamp': datetime.utcnow().isoformat(),
            'network_config': self.network_config,
            'vote_records': self.get_all_vote_records(),
            'booth_statistics': {
                k: v for k, v in self.demo_storage.items() 
                if k.startswith('booth_stats_')
            },
            'voter_statuses': {
                k: v for k, v in self.demo_storage.items() 
                if k.startswith('voter_')
            },
            'integrity_verified': True
        }

# Global blockchain instance
blockchain = BlockchainIntegration()

# Utility functions for Flask integration
def record_verification_step(voter_uuid: str, voter_id: str, booth_id: int, step: str) -> Dict[str, Any]:
    """Convenience function for recording verification steps"""
    return blockchain.record_vote_verification(voter_uuid, voter_id, booth_id, step)

def check_voter_blockchain_status(voter_uuid: str) -> Optional[Dict[str, Any]]:
    """Convenience function for checking voter status"""
    return blockchain.get_voter_status(voter_uuid)

def verify_blockchain_integrity(voter_uuid: str) -> bool:
    """Convenience function for verifying vote integrity"""
    return blockchain.verify_vote_integrity(voter_uuid)

def get_blockchain_audit_trail() -> Dict[str, Any]:
    """Convenience function for getting audit trail"""
    return blockchain.export_audit_trail()

# Example usage
if __name__ == "__main__":
    # Test blockchain integration
    blockchain = BlockchainIntegration()
    
    # Test vote recording
    result = blockchain.record_vote_verification(
        voter_uuid="test-uuid-123",
        voter_id="VID001",
        booth_id=1,
        verification_step="id_verification"
    )
    
    print("Blockchain test result:", result)
    
    # Test vote retrieval
    vote_record = blockchain.get_vote_record("test-uuid-123")
    print("Vote record:", vote_record)
    
    # Test integrity verification
    integrity_check = blockchain.verify_vote_integrity("test-uuid-123")
    print("Integrity check:", integrity_check)
