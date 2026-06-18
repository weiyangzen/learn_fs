<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/timeout/valid/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/timeout/valid/runtest.sh

## Purpose
Valid timeout semantics test for keys and keyrings, including expiration, revoked-key behavior, and expired-key operation failures.

## Important APIs, Types, And Functions
Uses `create_keyring`, `create_key`, `timeout_key`, `sleep_at_least`, `print_key`, `revoke_key`, `invalidate_key`, `list_keyring`, `describe_key`, `unlink_key`, and version-gated `expect_error`.

## Control Flow
Creates a key, proves a long timeout does not break reads, sets a short timeout and waits, verifies expired read/revoke/timeout failures, repeats with a revoked key, then expires the keyring and checks list/describe/timeout/invalidate/revoke failures.

## State And Persistence Behavior
Persists expiry timers in kernel key objects. The test intentionally waits for wall-clock expiry and relies on the session keyring to hold references until cleanup.

## Dependencies And Integration Points
The script depends on `prepare.inc.sh` for session-keyring setup, version/capability probes, and `$OUTPUTFILE`, and on `toolbox.inc.sh` for keyctl wrappers, marker logging, failure recording, error matching, and optional watch-notification checks.

## Risks And Edge Cases
Timing is inherently race-prone, mitigated by `sleep_at_least`. Expected expired-key errno differs on older kernels and RHEL7 backports.

## Test Signals
Signals include successful pre-expiry reads, `EKEYEXPIRED` or legacy `ENOKEY` after expiry, `EKEYREVOKED` after revocation, and expired-keyring failures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/timeout/valid/runtest.sh -->
