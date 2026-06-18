# sources/security-integrity/fscrypt/cli-tests/t_encrypt_raw_key.sh

## Purpose
Tests encryption using raw 256-bit key protectors.

## Control Flow and Integration
Creates random 32-byte keys and encrypts from file and stdin, verifies wrong 16-byte keys fail from file and stdin, then encrypts with a raw key file, locks, unlocks from stdin, and checks status.

## State and Risks
Exercises `makeRawKey`, `promptForKeyFile`, fixed-length key reads, raw key protector metadata, and key-file length validation.

## Test Signals
Validates both supported raw-key input modes and negative length checks.
