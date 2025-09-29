# Vote Authentication Blockchain

This directory contains the Hyperledger Fabric smart contract (chaincode) for the Election Vote Authentication System.

## Overview

The blockchain component provides:
- Immutable vote recording
- Fraud prevention through duplicate vote detection
- Audit trail for all voting activities
- Secure verification step tracking
- Real-time polling booth statistics

## Smart Contract Functions

### Core Functions

1. **RecordVoteVerification**
   - Records each verification step (ID, Face, Iris, Vote Cast)
   - Prevents duplicate voting
   - Updates voter status and booth statistics

2. **GetVoteRecord**
   - Retrieves complete vote record for a voter
   - Used for verification and audit purposes

3. **GetVoterStatus**
   - Checks if voter has already voted
   - Returns voting status and booth information

4. **GetPollingBoothStats**
   - Provides real-time statistics for polling booths
   - Tracks total votes cast per booth

### Audit Functions

5. **GetAllVoteRecords**
   - Retrieves all vote records for system-wide audit
   - Used by election commission for transparency

6. **VerifyVoteIntegrity**
   - Verifies the integrity of vote records using blockchain hashes
   - Ensures data hasn't been tampered with

7. **GetVoteHistory**
   - Retrieves voting history for specific voter ID
   - Supports audit and investigation processes

## Data Structures

### VoteRecord
```go
type VoteRecord struct {
    VoterUUID       string    `json:"voter_uuid"`
    VoterID         string    `json:"voter_id"`
    PollingBoothID  int       `json:"polling_booth_id"`
    Timestamp       time.Time `json:"timestamp"`
    IDVerified      bool      `json:"id_verified"`
    FaceVerified    bool      `json:"face_verified"`
    IrisVerified    bool      `json:"iris_verified"`
    VoteCast        bool      `json:"vote_cast"`
    BlockchainHash  string    `json:"blockchain_hash"`
    PreviousHash    string    `json:"previous_hash"`
}
```

### VoterStatus
```go
type VoterStatus struct {
    VoterUUID      string    `json:"voter_uuid"`
    VoterID        string    `json:"voter_id"`
    HasVoted       bool      `json:"has_voted"`
    VotedAt        time.Time `json:"voted_at"`
    PollingBoothID int       `json:"polling_booth_id"`
}
```

### PollingBoothStats
```go
type PollingBoothStats struct {
    BoothID     int       `json:"booth_id"`
    TotalVotes  int       `json:"total_votes"`
    LastUpdated time.Time `json:"last_updated"`
}
```

## Security Features

1. **Immutable Records**: Once written to blockchain, vote records cannot be modified
2. **Hash Verification**: Each record includes a cryptographic hash for integrity verification
3. **Duplicate Prevention**: Smart contract prevents multiple votes from same voter
4. **Audit Trail**: Complete history of all voting activities is maintained
5. **Access Control**: Only authorized nodes can participate in the network

## Deployment

### Prerequisites
- Hyperledger Fabric 2.4+
- Go 1.19+
- Docker and Docker Compose

### Build and Deploy
```bash
# Build the chaincode
go mod tidy
go build

# Package the chaincode
peer lifecycle chaincode package vote-auth.tar.gz --path . --lang golang --label vote-auth_1.0

# Install on peer
peer lifecycle chaincode install vote-auth.tar.gz

# Approve and commit (organization-specific commands)
peer lifecycle chaincode approveformyorg --channelID mychannel --name vote-auth --version 1.0 --package-id <package-id> --sequence 1

peer lifecycle chaincode commit --channelID mychannel --name vote-auth --version 1.0 --sequence 1
```

### Testing
```bash
# Initialize the ledger
peer chaincode invoke -o orderer.example.com:7050 --channelID mychannel -n vote-auth -c '{"function":"InitLedger","Args":[]}'

# Record a verification step
peer chaincode invoke -o orderer.example.com:7050 --channelID mychannel -n vote-auth -c '{"function":"RecordVoteVerification","Args":["voter-uuid-123","VID001","1","id_verification"]}'

# Query voter status
peer chaincode query -C mychannel -n vote-auth -c '{"function":"GetVoterStatus","Args":["voter-uuid-123"]}'
```

## Integration with Backend

The Flask backend integrates with this blockchain through Hyperledger Fabric SDK:

```python
# Example integration (simplified)
from hfc.fabric import Client

def record_vote_verification(voter_uuid, voter_id, booth_id, step):
    client = Client(net_profile="network.json")
    org1_admin = client.get_user(org_name='Org1', name='Admin')
    
    response = client.chaincode_invoke(
        requestor=org1_admin,
        channel_name='mychannel',
        peers=['peer0.org1.example.com'],
        cc_name='vote-auth',
        fcn='RecordVoteVerification',
        args=[voter_uuid, voter_id, str(booth_id), step]
    )
    
    return response
```

## Monitoring and Analytics

The blockchain provides real-time data for:
- Vote counting and verification
- Fraud attempt tracking
- Polling booth performance metrics
- System-wide audit capabilities

## Future Enhancements

1. **Advanced Cryptography**: Implement zero-knowledge proofs for privacy
2. **Multi-Signature**: Require multiple authorities for critical operations
3. **Automated Compliance**: Smart contract-based regulatory compliance
4. **Cross-Chain Integration**: Connect with other election systems
5. **AI-Powered Analytics**: Machine learning for fraud pattern detection

## Support

For technical support and documentation:
- Hyperledger Fabric Documentation: https://hyperledger-fabric.readthedocs.io/
- Smart Contract Development Guide: https://hyperledger-fabric.readthedocs.io/en/latest/smartcontract/smartcontract.html
