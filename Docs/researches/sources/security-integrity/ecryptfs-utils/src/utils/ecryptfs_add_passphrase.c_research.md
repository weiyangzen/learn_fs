<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_add_passphrase.c -->
# sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_add_passphrase.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_add_passphrase.c_research.md`. Source lines read for this pass: 124.

## Purpose
CLI utility that reads a passphrase and inserts a password auth token into the user session keyring, optionally also adding a filename-encryption key.

## Important APIs, Types, And Functions
Defines `usage` and `main`; calls `ecryptfs_get_passphrase`, `ecryptfs_get_version`, `ecryptfs_supports_filename_encryption`, `ecryptfs_read_salt_hex_from_rc`, and `ecryptfs_add_passphrase_key_to_keyring`.

## Control Flow
Supports interactive or stdin passphrase input and optional `--fnek`. It validates length, checks kernel FNEK support if requested, reads configured salt or defaults, inserts the FEK auth token, and for `--fnek` inserts a second token with the FNEK salt.

## State And Persistence Behavior
Changes kernel user/session keyring state and prints inserted signatures; reads eCryptfs rc salt.

## Dependencies And Integration Points
Depends on libecryptfs, kernel keyring support, and eCryptfs kernel version reporting.

## Risks And Edge Cases
Passphrases can flow through stdin pipelines. FNEK mode depends on kernel feature detection; failure after FEK insertion but before FNEK insertion can leave partial state.

## Test Signals
Used heavily by setup/mount scripts. Test with stdin and interactive modes, `--fnek`, invalid passphrase lengths, and keyctl signature lookup.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_add_passphrase.c -->
