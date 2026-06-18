<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/update/noargs/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/update/noargs/runtest.sh

## Purpose
Negative argument-count test for `keyctl update`.

## Important APIs, Types, And Functions
Uses `expect_args_error keyctl update` for zero, one, and three arguments.

## Control Flow
Runs invalid arities and reports the final result.

## State And Persistence Behavior
No key state is created.

## Dependencies And Integration Points
The script depends on `prepare.inc.sh` for session-keyring setup, version/capability probes, and `$OUTPUTFILE`, and on `toolbox.inc.sh` for keyctl wrappers, marker logging, failure recording, error matching, and optional watch-notification checks.

## Risks And Edge Cases
This only verifies CLI usage status, not payload parsing or kernel update behavior.

## Test Signals
Signals are exit-status 2 for bad update argument counts.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/update/noargs/runtest.sh -->
