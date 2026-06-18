# sources/security-integrity/fscrypt/cli-tests/t_status.sh

## Purpose
Tests global, mountpoint, and directory status output when a filesystem is set up or not set up.

## Control Flow and Integration
Captures enabled/setup counts, checks global and mountpoint status as root and test user, verifies unencrypted directory status fails, removes `.fscrypt` metadata, verifies setup count decreases while enabled count remains, then verifies mountpoint and directory status failures on the not-setup filesystem.

## State and Risks
Depends on stable status table columns and helper parsing. Mutates metadata directory to simulate not-setup state.

## Test Signals
Covers `writeGlobalStatus`, `writeFilesystemStatus`, and error paths for unencrypted paths and not-setup mounts.
