<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/search/bad-args/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/search/bad-args/runtest.sh

## Purpose
Bad-argument and invalid-search test for `keyctl search`. It covers malformed types/descriptions, invalid destination key IDs, and attempting to search a non-keyring key.

## Important APIs, Types, And Functions
Uses `search_for_key --fail`, `expect_error`, `create_key`, `unlink_key`, and version helpers such as `kernel_at_or_later_than` for MIPS/kernel-specific overlong description behavior.

## Control Flow
Runs invalid key type cases, max/overlong type and description cases, a bad destination ID case, creates a plain user key, confirms searching it as a keyring returns `ENOTDIR`, then unlinks it.

## State And Persistence Behavior
Creates one temporary user key in the session keyring. Otherwise state is transient command failure output plus `$OUTPUTFILE` diagnostics.

## Dependencies And Integration Points
The script depends on `prepare.inc.sh` for session-keyring setup, version/capability probes, and `$OUTPUTFILE`, and on `toolbox.inc.sh` for keyctl wrappers, marker logging, failure recording, error matching, and optional watch-notification checks.

## Risks And Edge Cases
Some overlong description assertions are gated for older MIPS kernels due to known kernel bugs. The distinction between `ENOKEY`, `EINVAL`, `EPERM`, and `ENOTDIR` is version and kernel-policy sensitive.

## Test Signals
Signals are exact errno mapping for invalid type, invalid length, invalid key ID, and non-keyring search roots.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/search/bad-args/runtest.sh -->
