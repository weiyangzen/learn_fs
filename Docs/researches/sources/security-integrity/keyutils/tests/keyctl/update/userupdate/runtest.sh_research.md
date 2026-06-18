<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/update/userupdate/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/update/userupdate/runtest.sh

## Purpose
Valid user-key update test, including ordinary string payloads and hex-encoded input.

## Important APIs, Types, And Functions
Uses `create_key`, `print_key`, `update_key`, `update_key -x`, `expect_payload`, and `unlink_key`.

## Control Flow
Creates a `user` key with payload `stuff`, reads it back, updates to `lizard`, reads again, updates with spaced hex data, reads `lizardx`, then unlinks the key.

## State And Persistence Behavior
Mutates a single user key payload in the session keyring. Payload state persists until the key is unlinked.

## Dependencies And Integration Points
The script depends on `prepare.inc.sh` for session-keyring setup, version/capability probes, and `$OUTPUTFILE`, and on `toolbox.inc.sh` for keyctl wrappers, marker logging, failure recording, error matching, and optional watch-notification checks.

## Risks And Edge Cases
Only user keys are covered. It does not test binary NUL payloads, large payloads, pupdate, permissions, or quota errors.

## Test Signals
Signals are exact payload transitions from `stuff` to `lizard` to `lizardx`.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/update/userupdate/runtest.sh -->
