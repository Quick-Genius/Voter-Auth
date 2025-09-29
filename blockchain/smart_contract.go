package main

import (
	"encoding/json"
	"fmt"
	"time"

	"github.com/hyperledger/fabric-contract-api-go/contractapi"
)

// VoteAuthContract provides functions for managing vote authentication
type VoteAuthContract struct {
	contractapi.Contract
}

// VoteRecord represents a vote record on the blockchain
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

// VoterStatus represents the current status of a voter
type VoterStatus struct {
	VoterUUID      string    `json:"voter_uuid"`
	VoterID        string    `json:"voter_id"`
	HasVoted       bool      `json:"has_voted"`
	VotedAt        time.Time `json:"voted_at"`
	PollingBoothID int       `json:"polling_booth_id"`
}

// PollingBoothStats represents statistics for a polling booth
type PollingBoothStats struct {
	BoothID     int `json:"booth_id"`
	TotalVotes  int `json:"total_votes"`
	LastUpdated time.Time `json:"last_updated"`
}

// InitLedger adds a base set of data to the ledger
func (s *VoteAuthContract) InitLedger(ctx contractapi.TransactionContextInterface) error {
	// Initialize with empty state
	return nil
}

// RecordVoteVerification records a vote verification step on the blockchain
func (s *VoteAuthContract) RecordVoteVerification(ctx contractapi.TransactionContextInterface, voterUUID string, voterID string, pollingBoothID int, verificationStep string) error {
	// Check if voter has already voted
	voterStatusJSON, err := ctx.GetStub().GetState(fmt.Sprintf("voter_%s", voterUUID))
	if err != nil {
		return fmt.Errorf("failed to read voter status: %v", err)
	}

	var voterStatus VoterStatus
	if voterStatusJSON != nil {
		err = json.Unmarshal(voterStatusJSON, &voterStatus)
		if err != nil {
			return fmt.Errorf("failed to unmarshal voter status: %v", err)
		}

		if voterStatus.HasVoted {
			return fmt.Errorf("voter %s has already voted", voterID)
		}
	} else {
		// Initialize voter status
		voterStatus = VoterStatus{
			VoterUUID:      voterUUID,
			VoterID:        voterID,
			HasVoted:       false,
			PollingBoothID: pollingBoothID,
		}
	}

	// Get or create vote record
	voteRecordKey := fmt.Sprintf("vote_%s", voterUUID)
	voteRecordJSON, err := ctx.GetStub().GetState(voteRecordKey)
	if err != nil {
		return fmt.Errorf("failed to read vote record: %v", err)
	}

	var voteRecord VoteRecord
	if voteRecordJSON != nil {
		err = json.Unmarshal(voteRecordJSON, &voteRecord)
		if err != nil {
			return fmt.Errorf("failed to unmarshal vote record: %v", err)
		}
	} else {
		// Create new vote record
		voteRecord = VoteRecord{
			VoterUUID:      voterUUID,
			VoterID:        voterID,
			PollingBoothID: pollingBoothID,
			Timestamp:      time.Now(),
		}
	}

	// Update verification status based on step
	switch verificationStep {
	case "id_verification":
		voteRecord.IDVerified = true
	case "face_verification":
		voteRecord.FaceVerified = true
	case "iris_verification":
		voteRecord.IrisVerified = true
	case "vote_cast":
		if !voteRecord.IDVerified || !voteRecord.FaceVerified || !voteRecord.IrisVerified {
			return fmt.Errorf("all verification steps must be completed before casting vote")
		}
		voteRecord.VoteCast = true
		voterStatus.HasVoted = true
		voterStatus.VotedAt = time.Now()
	default:
		return fmt.Errorf("invalid verification step: %s", verificationStep)
	}

	// Generate blockchain hash
	voteRecord.BlockchainHash = s.generateHash(voteRecord)

	// Store updated vote record
	voteRecordJSON, err = json.Marshal(voteRecord)
	if err != nil {
		return fmt.Errorf("failed to marshal vote record: %v", err)
	}

	err = ctx.GetStub().PutState(voteRecordKey, voteRecordJSON)
	if err != nil {
		return fmt.Errorf("failed to put vote record: %v", err)
	}

	// Store updated voter status
	voterStatusJSON, err = json.Marshal(voterStatus)
	if err != nil {
		return fmt.Errorf("failed to marshal voter status: %v", err)
	}

	err = ctx.GetStub().PutState(fmt.Sprintf("voter_%s", voterUUID), voterStatusJSON)
	if err != nil {
		return fmt.Errorf("failed to put voter status: %v", err)
	}

	// Update polling booth statistics if vote was cast
	if verificationStep == "vote_cast" {
		err = s.updatePollingBoothStats(ctx, pollingBoothID)
		if err != nil {
			return fmt.Errorf("failed to update polling booth stats: %v", err)
		}
	}

	return nil
}

// GetVoteRecord retrieves a vote record by voter UUID
func (s *VoteAuthContract) GetVoteRecord(ctx contractapi.TransactionContextInterface, voterUUID string) (*VoteRecord, error) {
	voteRecordJSON, err := ctx.GetStub().GetState(fmt.Sprintf("vote_%s", voterUUID))
	if err != nil {
		return nil, fmt.Errorf("failed to read vote record: %v", err)
	}

	if voteRecordJSON == nil {
		return nil, fmt.Errorf("vote record for voter %s does not exist", voterUUID)
	}

	var voteRecord VoteRecord
	err = json.Unmarshal(voteRecordJSON, &voteRecord)
	if err != nil {
		return nil, fmt.Errorf("failed to unmarshal vote record: %v", err)
	}

	return &voteRecord, nil
}

// GetVoterStatus retrieves voter status by voter UUID
func (s *VoteAuthContract) GetVoterStatus(ctx contractapi.TransactionContextInterface, voterUUID string) (*VoterStatus, error) {
	voterStatusJSON, err := ctx.GetStub().GetState(fmt.Sprintf("voter_%s", voterUUID))
	if err != nil {
		return nil, fmt.Errorf("failed to read voter status: %v", err)
	}

	if voterStatusJSON == nil {
		return nil, fmt.Errorf("voter status for %s does not exist", voterUUID)
	}

	var voterStatus VoterStatus
	err = json.Unmarshal(voterStatusJSON, &voterStatus)
	if err != nil {
		return nil, fmt.Errorf("failed to unmarshal voter status: %v", err)
	}

	return &voterStatus, nil
}

// GetPollingBoothStats retrieves statistics for a polling booth
func (s *VoteAuthContract) GetPollingBoothStats(ctx contractapi.TransactionContextInterface, boothID int) (*PollingBoothStats, error) {
	statsJSON, err := ctx.GetStub().GetState(fmt.Sprintf("booth_stats_%d", boothID))
	if err != nil {
		return nil, fmt.Errorf("failed to read booth stats: %v", err)
	}

	if statsJSON == nil {
		// Return empty stats if not found
		return &PollingBoothStats{
			BoothID:     boothID,
			TotalVotes:  0,
			LastUpdated: time.Now(),
		}, nil
	}

	var stats PollingBoothStats
	err = json.Unmarshal(statsJSON, &stats)
	if err != nil {
		return nil, fmt.Errorf("failed to unmarshal booth stats: %v", err)
	}

	return &stats, nil
}

// GetAllVoteRecords retrieves all vote records (for audit purposes)
func (s *VoteAuthContract) GetAllVoteRecords(ctx contractapi.TransactionContextInterface) ([]*VoteRecord, error) {
	resultsIterator, err := ctx.GetStub().GetStateByRange("vote_", "vote_~")
	if err != nil {
		return nil, fmt.Errorf("failed to get vote records: %v", err)
	}
	defer resultsIterator.Close()

	var voteRecords []*VoteRecord
	for resultsIterator.HasNext() {
		queryResponse, err := resultsIterator.Next()
		if err != nil {
			return nil, fmt.Errorf("failed to iterate vote records: %v", err)
		}

		var voteRecord VoteRecord
		err = json.Unmarshal(queryResponse.Value, &voteRecord)
		if err != nil {
			return nil, fmt.Errorf("failed to unmarshal vote record: %v", err)
		}
		voteRecords = append(voteRecords, &voteRecord)
	}

	return voteRecords, nil
}

// VerifyVoteIntegrity verifies the integrity of a vote record
func (s *VoteAuthContract) VerifyVoteIntegrity(ctx contractapi.TransactionContextInterface, voterUUID string) (bool, error) {
	voteRecord, err := s.GetVoteRecord(ctx, voterUUID)
	if err != nil {
		return false, err
	}

	// Recalculate hash and compare
	expectedHash := s.generateHash(*voteRecord)
	return voteRecord.BlockchainHash == expectedHash, nil
}

// Helper function to update polling booth statistics
func (s *VoteAuthContract) updatePollingBoothStats(ctx contractapi.TransactionContextInterface, boothID int) error {
	statsKey := fmt.Sprintf("booth_stats_%d", boothID)
	statsJSON, err := ctx.GetStub().GetState(statsKey)
	if err != nil {
		return fmt.Errorf("failed to read booth stats: %v", err)
	}

	var stats PollingBoothStats
	if statsJSON != nil {
		err = json.Unmarshal(statsJSON, &stats)
		if err != nil {
			return fmt.Errorf("failed to unmarshal booth stats: %v", err)
		}
	} else {
		stats = PollingBoothStats{
			BoothID:    boothID,
			TotalVotes: 0,
		}
	}

	stats.TotalVotes++
	stats.LastUpdated = time.Now()

	statsJSON, err = json.Marshal(stats)
	if err != nil {
		return fmt.Errorf("failed to marshal booth stats: %v", err)
	}

	return ctx.GetStub().PutState(statsKey, statsJSON)
}

// Helper function to generate a hash for vote record
func (s *VoteAuthContract) generateHash(voteRecord VoteRecord) string {
	// Simple hash generation - in production, use proper cryptographic hash
	data := fmt.Sprintf("%s_%s_%d_%v_%v_%v_%v",
		voteRecord.VoterUUID,
		voteRecord.VoterID,
		voteRecord.PollingBoothID,
		voteRecord.IDVerified,
		voteRecord.FaceVerified,
		voteRecord.IrisVerified,
		voteRecord.VoteCast,
	)
	
	// In production, use SHA-256 or similar
	return fmt.Sprintf("hash_%x", len(data)*17+42) // Simplified hash
}

// GetVoteHistory retrieves vote history for audit trail
func (s *VoteAuthContract) GetVoteHistory(ctx contractapi.TransactionContextInterface, voterID string) ([]*VoteRecord, error) {
	// Query by voter ID
	queryString := fmt.Sprintf(`{"selector":{"voter_id":"%s"}}`, voterID)
	
	resultsIterator, err := ctx.GetStub().GetQueryResult(queryString)
	if err != nil {
		return nil, fmt.Errorf("failed to query vote history: %v", err)
	}
	defer resultsIterator.Close()

	var voteRecords []*VoteRecord
	for resultsIterator.HasNext() {
		queryResponse, err := resultsIterator.Next()
		if err != nil {
			return nil, fmt.Errorf("failed to iterate vote history: %v", err)
		}

		var voteRecord VoteRecord
		err = json.Unmarshal(queryResponse.Value, &voteRecord)
		if err != nil {
			return nil, fmt.Errorf("failed to unmarshal vote record: %v", err)
		}
		voteRecords = append(voteRecords, &voteRecord)
	}

	return voteRecords, nil
}

func main() {
	voteAuthContract := new(VoteAuthContract)

	chaincode, err := contractapi.NewChaincode(voteAuthContract)
	if err != nil {
		fmt.Printf("Error creating vote auth chaincode: %s", err.Error())
		return
	}

	if err := chaincode.Start(); err != nil {
		fmt.Printf("Error starting vote auth chaincode: %s", err.Error())
	}
}
