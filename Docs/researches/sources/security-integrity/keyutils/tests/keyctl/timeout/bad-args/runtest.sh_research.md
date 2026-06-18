<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/timeout/bad-args/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/timeout/bad-args/runtest.sh

## Purpose
Bad-key-ID and missing-key test for `keyctl timeout`.

## Important APIs, Types, And Functions
Uses `timeout_key --fail`, `create_key`, `unlink_key --wait`, and `expect_error`.

## Control Flow
Checks key ID zero returns `EINVAL`, creates a user key, unlinks and waits for it to be unreachable, then checks setting timeout on the stale ID returns `ENOKEY`.

## State And Persistence Behavior
Creates and destroys one temporary user key. Lazy key destruction is handled through the toolbox wait path.

## Dependencies And Integration Points
The script depends on `prepare.inc.sh` for session-keyring setup, version/capability probes, and `$OUTPUTFILE`, and on `toolbox.inc.sh` for keyctl wrappers, marker logging, failure recording, error matching, and optional watch-notification checks.

## Risks And Edge Cases
The stale ID test depends on key garbage collection and the helper's wait loop making the ID unusable before timeout is attempted.

## Test Signals
Signals are `EINVAL` for key ID zero and `ENOKEY` for a destroyed key ID.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/timeout/bad-args/runtest.sh -->
