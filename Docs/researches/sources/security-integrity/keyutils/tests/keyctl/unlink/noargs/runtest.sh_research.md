<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/unlink/noargs/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/unlink/noargs/runtest.sh

## Purpose
Negative argument-count test for `keyctl unlink`.

## Important APIs, Types, And Functions
Uses `expect_args_error keyctl unlink`; the one-argument invalid case is only expected for keyutils older than 1.5 because newer versions support unlink-all.

## Control Flow
Checks no arguments, conditionally one argument, and three arguments.

## State And Persistence Behavior
No key state is created.

## Dependencies And Integration Points
The script depends on `prepare.inc.sh` for session-keyring setup, version/capability probes, and `$OUTPUTFILE`, and on `toolbox.inc.sh` for keyctl wrappers, marker logging, failure recording, error matching, and optional watch-notification checks.

## Risks And Edge Cases
Version-gated behavior is central because one argument changed from invalid syntax to a valid operation.

## Test Signals
Signals are bad-arity exit status for unsupported arities.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/unlink/noargs/runtest.sh -->
