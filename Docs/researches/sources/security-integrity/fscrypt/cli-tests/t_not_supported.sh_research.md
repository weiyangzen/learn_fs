# sources/security-integrity/fscrypt/cli-tests/t_not_supported.sh

## Purpose
Tests behavior on a filesystem that does not support fscrypt encryption.

## Control Flow and Integration
Unmounts the ext4 test mount, mounts tmpfs, verifies `fscrypt setup` fails on tmpfs, creates a directory, and verifies `fscrypt encrypt` fails.

## State and Risks
Exercises `filesystem.ErrEncryptionNotSupported` paths and generic support suggestions.

## Test Signals
Confirms fscrypt does not create metadata or apply policies on unsupported filesystems.
