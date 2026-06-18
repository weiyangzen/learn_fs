# sources/security-integrity/fscrypt/cli-tests/t_encrypt.sh

## Purpose
General integration tests for `fscrypt encrypt` independent of protector-specific variants.

## Control Flow and Integration
Defines reset/status helpers, then verifies encryption fails for nonexistent and nonempty directories, including trailing slash. It tests successful encryption by non-root owner with named protector, status visibility for root and user, rejection of re-encrypting an encrypted directory, and rejection when a non-root user tries to encrypt another user's directory.

## State and Risks
Mutates directory ownership and metadata. It covers precondition checks in `checkEncryptable`, context trust rules, and permissions.

## Test Signals
Strong signal for user-facing encrypt validation and error formatting through status checks and expected failures.
