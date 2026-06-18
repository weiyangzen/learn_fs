# sources/security-integrity/fscrypt/cli-tests/t_lock.sh

## Purpose
Tests `fscrypt lock` behavior under normal, busy-file, cross-user, and loose-file conditions.

## Control Flow and Integration
Encrypts a directory, writes a file, locks it and verifies ciphertext/no-create behavior, unlocks and verifies contents, tries locking while a file descriptor is open and checks incomplete status, finishes locking after closing the file, tests locking while another user has unlocked and then with `--all-users`, and verifies operations fail on a locked loose regular file.

## State and Risks
Exercises kernel key removal, files-busy detection, status heuristics, all-users deprovisioning, and `metadata.ErrLockedRegularFile` error handling.

## Test Signals
Important end-to-end signal for keyring removal semantics and user-facing partial-lock diagnostics.
