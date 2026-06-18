<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/watch/noargs/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/watch/noargs/runtest.sh

## Purpose
Negative argument-count and malformed-filter test for `keyctl watch`.

## Important APIs, Types, And Functions
Uses `expect_args_error keyctl watch` and `expect_args_error keyctl watch_key -f 0`.

## Control Flow
Checks no arguments, too many object arguments, and a bad filter option.

## State And Persistence Behavior
No key state is created; only CLI parsing output is logged.

## Dependencies And Integration Points
The script depends on `prepare.inc.sh` for session-keyring setup, version/capability probes, and `$OUTPUTFILE`, and on `toolbox.inc.sh` for keyctl wrappers, marker logging, failure recording, error matching, and optional watch-notification checks.

## Risks And Edge Cases
The last command names `watch_key`, which may be a compatibility alias or typo-sensitive path depending on keyutils CLI behavior.

## Test Signals
Signals are bad-arity and bad-filter usage failures.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/watch/noargs/runtest.sh -->
