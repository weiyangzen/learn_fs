<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/session/valid/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/session/valid/runtest.sh

## Purpose
Valid `keyctl session` test for anonymous and named session keyrings.

## Important APIs, Types, And Functions
Uses `new_session`, `keyctl rdescribe @s`, `expect_key_rdesc`, distro/version helpers, and output parsing with `tail`, `head`, and `expr`.

## Control Flow
On old RHEL it checks anonymous session creation. It always creates a named session `qwerty`, validates the raw session keyring description, and verifies that `Joined session keyring: <id>` was printed.

## State And Persistence Behavior
Creates child session keyrings for the subprocess command. The parent test process state is not replaced because `keyctl session` runs the supplied command in the new session.

## Dependencies And Integration Points
The script depends on `prepare.inc.sh` for session-keyring setup, version/capability probes, and `$OUTPUTFILE`, and on `toolbox.inc.sh` for keyctl wrappers, marker logging, failure recording, error matching, and optional watch-notification checks.

## Risks And Edge Cases
Anonymous-session coverage is distro-gated. The test depends on stable human-readable `keyctl session` output format and raw-description naming.

## Test Signals
Signals are the expected session keyring description pattern and visible joined keyring ID.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/session/valid/runtest.sh -->
