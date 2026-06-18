# sources/security-integrity/fscrypt/cli-tests/t_metadata.sh

## Purpose
Tests advanced `fscrypt metadata` operations for manual protector and policy management.

## Control Flow and Integration
Creates three custom protectors, creates a policy with one protector, adds two more protectors using different unlock paths, displays status, removes two protectors from the policy, deletes one protector metadata file before removal to ensure policy update still works, and displays status again.

## State and Risks
Directly manipulates `.fscrypt` metadata and tests `AddProtector`/`RemoveProtector` command flows. Deleting a protector file simulates partial metadata loss.

## Test Signals
Provides coverage for multi-protector policies and force removal from policy even with missing protector metadata.
