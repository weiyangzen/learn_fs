<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/update/bad-args/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/update/bad-args/runtest.sh

## Purpose
Bad-object test for `keyctl update`.

## Important APIs, Types, And Functions
Uses `update_key --fail`, `create_key`, `unlink_key --wait`, and `expect_error`.

## Control Flow
Confirms updating the session keyring returns `EOPNOTSUPP`, invalid key ID zero returns `EINVAL`, and updating a destroyed user key returns `ENOKEY`.

## State And Persistence Behavior
Creates and destroys one temporary user key. No lasting key payload is retained.

## Dependencies And Integration Points
The script depends on `prepare.inc.sh` for session-keyring setup, version/capability probes, and `$OUTPUTFILE`, and on `toolbox.inc.sh` for keyctl wrappers, marker logging, failure recording, error matching, and optional watch-notification checks.

## Risks And Edge Cases
The test assumes keyrings do not support update and that stale ID cleanup completes before the final update attempt.

## Test Signals
Signals are `EOPNOTSUPP`, `EINVAL`, and `ENOKEY` for unsupported, invalid, and stale update targets.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/update/bad-args/runtest.sh -->
