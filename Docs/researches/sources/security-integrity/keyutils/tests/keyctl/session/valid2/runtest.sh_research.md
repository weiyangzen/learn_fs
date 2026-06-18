<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/session/valid2/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/session/valid2/runtest.sh

## Purpose
Valid `keyctl new_session` test that replaces the running script's session keyring and confirms IDs change.

## Important APIs, Types, And Functions
Uses `id_key --to`, `new_session_to_parent`, `describe_key`, and `expect_key_rdesc`.

## Control Flow
Captures the original session keyring ID, creates an anonymous replacement and checks the ID differs, then creates a named replacement `lizard` and checks it differs from both earlier IDs.

## State And Persistence Behavior
Mutates the current process/session keyring association rather than just a child process. The session keyring persists for the remainder of the test process.

## Dependencies And Integration Points
The script depends on `prepare.inc.sh` for session-keyring setup, version/capability probes, and `$OUTPUTFILE`, and on `toolbox.inc.sh` for keyctl wrappers, marker logging, failure recording, error matching, and optional watch-notification checks.

## Risks And Edge Cases
The script assumes the session keyring ID changes on every successful replacement and that names `_ses` and `lizard` appear in raw descriptions.

## Test Signals
Signals are changed keyring IDs and matching anonymous/named keyring descriptions.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/session/valid2/runtest.sh -->
