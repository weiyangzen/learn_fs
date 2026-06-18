<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/watch/bad-args/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/watch/bad-args/runtest.sh

## Purpose
Bad-object and bad-filter test for `keyctl watch` when notification support is available.

## Important APIs, Types, And Functions
Uses `have_notify` gating, `watch_key --fail/--fail2`, `create_key`, `unlink_key --wait`, and `expect_error`.

## Control Flow
Skips if notifications are unavailable. Otherwise it checks invalid key ID zero, stale key ID after unlink, and malformed filter options.

## State And Persistence Behavior
Creates and destroys one user key. Watch command failures should not add lasting watches; output may touch `notify.log` through the toolbox wrapper.

## Dependencies And Integration Points
The script depends on `prepare.inc.sh` for session-keyring setup, version/capability probes, and `$OUTPUTFILE`, and on `toolbox.inc.sh` for keyctl wrappers, marker logging, failure recording, error matching, and optional watch-notification checks.

## Risks And Edge Cases
The test is skipped without notification support. Filter parsing expects specific exit status 2 through `--fail2` but does not assert text.

## Test Signals
Signals are `EINVAL`, `ENOKEY`, and bad-filter exit status for watch setup failures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/watch/bad-args/runtest.sh -->
