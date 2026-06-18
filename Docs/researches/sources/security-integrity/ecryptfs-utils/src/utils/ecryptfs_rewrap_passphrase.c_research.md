<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_rewrap_passphrase.c -->
# sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_rewrap_passphrase.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_rewrap_passphrase.c_research.md`. Source lines read for this pass: 108.

## Purpose
Changes the wrapping passphrase protecting an existing eCryptfs wrapped mount passphrase.

## Important APIs, Types, And Functions
Defines `usage` and `main`; uses `ecryptfs_get_passphrase`, `ecryptfs_unwrap_passphrase`, `ecryptfs_wrap_passphrase`, and salt loading.

## Control Flow
Reads old and new wrapping passphrases interactively, from stdin, or from argv. Interactive mode requires new passphrase confirmation. It unwraps the mount passphrase with the old wrapping passphrase, then writes the same mount passphrase rewrapped with the new wrapping passphrase.

## State And Persistence Behavior
Overwrites the wrapped-passphrase file. The unwrapped mount passphrase lives transiently in stack memory.

## Dependencies And Integration Points
Depends on libecryptfs wrapping APIs and configured salt semantics.

## Risks And Edge Cases
Argument mode exposes secrets. There is no explicit secure zeroing of stack passphrase after use, and interruption while writing could corrupt the wrapped file depending on libecryptfs behavior.

## Test Signals
Test by wrapping a known mount passphrase, rewrapping, proving old password no longer unwraps and new password does.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_rewrap_passphrase.c -->
