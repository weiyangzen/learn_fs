<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_wrap_passphrase.c -->
# sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_wrap_passphrase.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_wrap_passphrase.c_research.md`. Source lines read for this pass: 97.

## Purpose
Creates or replaces an eCryptfs wrapped-passphrase file from a mount passphrase and wrapping passphrase.

## Important APIs, Types, And Functions
Defines `usage` and `main`; uses `ecryptfs_get_passphrase`, salt loading, and `ecryptfs_wrap_passphrase`.

## Control Flow
Accepts file path and passphrases interactively, via stdin, or via argv. It validates passphrase lengths, reads configured/default salt, and delegates file serialization/encryption to libecryptfs.

## State And Persistence Behavior
Writes the wrapped-passphrase file, usually under `~/.ecryptfs/wrapped-passphrase`.

## Dependencies And Integration Points
Depends on libecryptfs wrapping APIs and filesystem permissions around the target file.

## Risks And Edge Cases
Argument mode exposes both secrets. Callers must set restrictive umask/mode because this file protects access to encrypted data.

## Test Signals
Used by setup-private. Round-trip test with unwrap and insert-wrapped-passphrase into keyring is the key signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_wrap_passphrase.c -->
