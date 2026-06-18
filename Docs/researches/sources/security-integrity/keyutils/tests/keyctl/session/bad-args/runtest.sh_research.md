<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/session/bad-args/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/session/bad-args/runtest.sh

## Purpose
Bad-argument test for creating a new session keyring with invalid names.

## Important APIs, Types, And Functions
Uses `new_session --fail`, `expect_error`, `maxdesc`, and kernel/architecture version helpers.

## Control Flow
Checks empty keyring names with `EINVAL`; conditionally checks an overlong name on kernels/architectures where the bug is not expected.

## State And Persistence Behavior
No lasting key state is intentionally retained; child session creation attempts fail and output is logged.

## Dependencies And Integration Points
The script depends on `prepare.inc.sh` for session-keyring setup, version/capability probes, and `$OUTPUTFILE`, and on `toolbox.inc.sh` for keyctl wrappers, marker logging, failure recording, error matching, and optional watch-notification checks.

## Risks And Edge Cases
The overlong-name case is skipped on pre-3.19 MIPS/MIPS64 because kernel behavior is known to be buggy.

## Test Signals
Signals are `EINVAL` for empty and supported overlong keyring names.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/session/bad-args/runtest.sh -->
