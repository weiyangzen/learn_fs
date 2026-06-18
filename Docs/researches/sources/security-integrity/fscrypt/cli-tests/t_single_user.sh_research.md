# sources/security-integrity/fscrypt/cli-tests/t_single_user.sh

## Purpose
Tests filesystem setup without `--all-users`, where only the setup user can create fscrypt metadata.

## Control Flow and Integration
Recreates root/data metadata and config in single-user mode, checks status as root and user, encrypts/locks/unlocks as root, encrypts as root with user's login protector and verifies the user can update policy and unlock, verifies user encryption fails when root owns metadata, then chowns mount metadata and lets the user run setup and encrypt successfully.

## State and Risks
Exercises setup mode ownership, metadata update fallback permissions, login protector ownership, and non-root restrictions.

## Test Signals
Important coverage for single-user deployment and root-on-behalf-of-user ownership correctness.
