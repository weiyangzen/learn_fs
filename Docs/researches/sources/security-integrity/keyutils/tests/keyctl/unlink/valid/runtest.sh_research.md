<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/unlink/valid/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/unlink/valid/runtest.sh

## Purpose
Valid unlink behavior test for removing keys and keyrings from a keyring.

## Important APIs, Types, And Functions
Uses `create_keyring`, `create_key`, `list_keyring`, `unlink_key --wait`, `expect_keyring_rlist`, `expect_error`, and direct `keyctl show`.

## Control Flow
Creates a keyring and key, unlinks the key and verifies repeat unlink fails, then creates twenty keys and twenty keyrings, validates membership, unlinks each entry, and confirms the keyring is empty.

## State And Persistence Behavior
Exercises kernel keyring link membership and lazy destruction. Final cleanup unlinks the top keyring from the session keyring.

## Dependencies And Integration Points
The script depends on `prepare.inc.sh` for session-keyring setup, version/capability probes, and `$OUTPUTFILE`, and on `toolbox.inc.sh` for keyctl wrappers, marker logging, failure recording, error matching, and optional watch-notification checks.

## Risks And Edge Cases
Exact membership checks assume `rlist` output is stable. The test creates many objects and can be affected by key quota limits.

## Test Signals
Signals are membership before unlink, `ENOKEY` on repeated unlink, and empty `rlist` after deleting all contents.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/unlink/valid/runtest.sh -->
