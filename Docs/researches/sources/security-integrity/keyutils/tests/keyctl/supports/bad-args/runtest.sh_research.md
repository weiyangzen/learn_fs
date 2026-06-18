<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/supports/bad-args/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/supports/bad-args/runtest.sh

## Purpose
Negative arity test for `keyctl supports`.

## Important APIs, Types, And Functions
Uses `expect_args_error keyctl support` for two and three arguments. The path name says `supports`, but the CLI subcommand used here is `support`.

## Control Flow
Runs invalid two-argument and three-argument invocations and reports the shared result.

## State And Persistence Behavior
No kernel key state is changed.

## Dependencies And Integration Points
The script depends on `prepare.inc.sh` for session-keyring setup, version/capability probes, and `$OUTPUTFILE`, and on `toolbox.inc.sh` for keyctl wrappers, marker logging, failure recording, error matching, and optional watch-notification checks.

## Risks And Edge Cases
This is only CLI usage validation. It does not check the newer capability-query semantics.

## Test Signals
Signals are bad-arity exit status 2 for `keyctl support`.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/supports/bad-args/runtest.sh -->
