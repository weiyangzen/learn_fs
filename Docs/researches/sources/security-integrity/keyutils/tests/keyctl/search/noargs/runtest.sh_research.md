<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/search/noargs/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/search/noargs/runtest.sh

## Purpose
Negative argument-count test for `keyctl search`.

## Important APIs, Types, And Functions
Uses `expect_args_error keyctl search` for zero, one, two, and five arguments, with markers for each arity.

## Control Flow
Initializes the harness result, executes each invalid arity, and reports the final result.

## State And Persistence Behavior
No key objects are created. State is only test log output.

## Dependencies And Integration Points
The script depends on `prepare.inc.sh` for session-keyring setup, version/capability probes, and `$OUTPUTFILE`, and on `toolbox.inc.sh` for keyctl wrappers, marker logging, failure recording, error matching, and optional watch-notification checks.

## Risks And Edge Cases
Only CLI arity/exit-status behavior is covered; semantic search errors are covered in sibling tests.

## Test Signals
Signals are exit-status 2 for too-few and too-many `search` command arguments.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/search/noargs/runtest.sh -->
