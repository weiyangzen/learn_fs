# sources/security-integrity/fscrypt/actions/recovery_test.go

## Purpose
Tests recovery passphrase creation, usability, instruction file generation, and naming collisions.

## APIs and Control Flow
`TestRecoveryPassphrase` creates a protector/policy pair, calls `AddRecoveryPassphrase`, checks passphrase length and protector name, confirms the policy now has two protectors, unlocks the recovery protector with the generated passphrase, writes instructions, verifies the file contains the passphrase, then calls `AddRecoveryPassphrase` again and expects the ` (2)` suffix.

## State, Dependencies, and Integration
Uses real policy/protector metadata and a temp recovery file. It depends on shared action test fixtures and `crypto.Key.Clone` to unlock with the generated passphrase.

## Risks and Test Signals
The test confirms core recovery correctness but does not verify file mode, `O_NOFOLLOW`, ownership changes, or fsync behavior.
