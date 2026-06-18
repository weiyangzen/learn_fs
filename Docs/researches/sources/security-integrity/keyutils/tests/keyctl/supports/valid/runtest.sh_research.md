<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/supports/valid/runtest.sh -->
# sources/security-integrity/keyutils/tests/keyctl/supports/valid/runtest.sh

## Purpose
Valid feature-query test for `keyctl supports`.

## Important APIs, Types, And Functions
Uses the toolbox `supports` wrapper, including the `--unrecognised` mode that expects exit status 3.

## Control Flow
First lists supported capabilities, then queries an unrecognized capability name to confirm the wrapper accepts the expected nonzero status.

## State And Persistence Behavior
No key objects are created; it reads keyutils/kernel feature support and writes log output.

## Dependencies And Integration Points
The script depends on `prepare.inc.sh` for session-keyring setup, version/capability probes, and `$OUTPUTFILE`, and on `toolbox.inc.sh` for keyctl wrappers, marker logging, failure recording, error matching, and optional watch-notification checks.

## Risks And Edge Cases
Coverage is shallow: it does not assert specific capability variables, only command success and the unrecognized-query exit code.

## Test Signals
Signals are successful list operation and expected exit status for an unknown capability query.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/keyctl/supports/valid/runtest.sh -->
