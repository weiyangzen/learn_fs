<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_insert_wrapped_passphrase_into_keyring.c -->
# sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_insert_wrapped_passphrase_into_keyring.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_insert_wrapped_passphrase_into_keyring.c_research.md`. Source lines read for this pass: 98.

## Purpose
Unwraps a stored wrapped-passphrase file with a wrapping passphrase and inserts the resulting eCryptfs auth token into the user session keyring.

## Important APIs, Types, And Functions
Defines `usage` and `main`; calls `ecryptfs_get_wrapped_passphrase_filename`, `ecryptfs_get_passphrase`, `ecryptfs_read_salt_hex_from_rc`, and `ecryptfs_insert_wrapped_passphrase_into_keyring`.

## Control Flow
Supports default file interactive mode, explicit file interactive mode, stdin passphrase mode, and direct argument passphrase mode. It validates passphrase length, selects configured/default salt, calls libecryptfs to unwrap and insert, and prints the signature.

## State And Persistence Behavior
Reads a wrapped-passphrase file and writes to the kernel keyring; no file mutation.

## Dependencies And Integration Points
Depends on libecryptfs, configured per-user wrapped-passphrase path, and keyring support.

## Risks And Edge Cases
Direct argument mode exposes passphrases in process listings. This tool is central to private mount login behavior, so salt handling must match the wrapping path exactly.

## Test Signals
Setup-private and mount-private exercise it. Unit coverage should include default path, explicit path, stdin, bad passphrase, and missing file.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_insert_wrapped_passphrase_into_keyring.c -->
