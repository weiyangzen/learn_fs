<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/revoke/noargs/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/revoke/noargs/runtest.sh

## Purpose
Negative argument-count test for `keyctl revoke`. It validates command-line usage handling rather than kernel revocation semantics.

## Important APIs, Types, And Functions
Uses `expect_args_error keyctl revoke` for no arguments and for two arguments. `marker` records each phase and `toolbox_report_result` reports the shared `result` state.

## Control Flow
Initializes `result=PASS`, truncates `$OUTPUTFILE`, executes two invalid invocations, and finishes by appending the final status banner.

## State And Persistence Behavior
No keys are created. Persistent effects are limited to the per-test output log and optional RHTS result reporting.

## Dependencies And Integration Points
The script depends on `prepare.inc.sh` for session-keyring setup, version/capability probes, and `$OUTPUTFILE`, and on `toolbox.inc.sh` for keyctl wrappers, marker logging, failure recording, error matching, and optional watch-notification checks.

## Risks And Edge Cases
It only checks exit status 2 through `expect_args_error`; it does not assert exact usage text. A CLI that changes bad-argument exit codes would fail even if the kernel path is unchanged.

## Test Signals
Useful signals are no-argument and too-many-argument failures for the `revoke` subcommand.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/revoke/noargs/runtest.sh -->
