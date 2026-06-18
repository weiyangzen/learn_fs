<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_unwrap_passphrase.c -->
# sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_unwrap_passphrase.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_unwrap_passphrase.c_research.md`. Source lines read for this pass: 94.

## Purpose
Prints the unwrapped mount passphrase from a wrapped-passphrase file after receiving the wrapping passphrase.

## Important APIs, Types, And Functions
Defines `usage` and `main`; uses default wrapped-passphrase filename, `ecryptfs_get_passphrase`, salt loading, and `ecryptfs_unwrap_passphrase`.

## Control Flow
Supports default or explicit file, interactive or stdin/direct wrapping passphrase. It validates length, unwraps into a fixed-size buffer, and writes the plaintext mount passphrase to stdout.

## State And Persistence Behavior
Read-only on wrapped-passphrase file; exposes secret output intentionally for backup/recovery.

## Dependencies And Integration Points
Depends on libecryptfs and matching salt configuration.

## Risks And Edge Cases
Plaintext mount passphrase is emitted to stdout and may be captured in shell history, logs, pipes, or terminals. Direct argument mode exposes wrapping passphrase.

## Test Signals
Setup-private instructions rely on this. Test success, wrong passphrase, stdin mode, and default path resolution.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_unwrap_passphrase.c -->
