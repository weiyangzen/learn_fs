<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/show/noargs/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/show/noargs/runtest.sh

## Purpose
Default `keyctl show` test. It verifies that running without arguments shows the current session keyring in the expected textual layout.

## Important APIs, Types, And Functions
Invokes `keyctl show` directly, uses `wc`, `sed`, `grep`, `cut`, `awk`, `expr`, and shared `failed` handling.

## Control Flow
Runs `keyctl show`, requires enough output lines, checks the third line is `Session Keyring`, and verifies the first keyring listed is the RHTS/keyctl session keyring.

## State And Persistence Behavior
Does not create keys itself; it observes the session keyring created by `prepare.inc.sh`. State is output-format validation.

## Dependencies And Integration Points
The script depends on `prepare.inc.sh` for session-keyring setup, version/capability probes, and `$OUTPUTFILE`, and on `toolbox.inc.sh` for keyctl wrappers, marker logging, failure recording, error matching, and optional watch-notification checks.

## Risks And Edge Cases
Highly sensitive to `keyctl show` output layout, line numbers, field positions, and session naming convention.

## Test Signals
Signals are nonzero line count, the `Session Keyring` header, and an expected keyring name prefix.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/show/noargs/runtest.sh -->
