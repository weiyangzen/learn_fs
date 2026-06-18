<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/runtest.sh -->
# sources/security-integrity/keyutils/tests/runtest.sh

## Purpose
Top-level runner for keyutils tests. It iterates over test directories passed on the command line and invokes each `runtest.sh`.

## Important APIs, Types, And Functions
Uses `AUTOMATED`, `TESTS`, `TEST`, shell `pushd`/`popd`, and direct `bash ./runtest.sh`. It warns when not running as root because some tests need privileged behavior.

## Control Flow
For each requested test path it exports `TEST`, enters the directory, prints a running banner, and executes the local test. In non-automated mode the first failing test stops the suite; in automated mode it continues.

## State And Persistence Behavior
No kernel state is directly changed by this file; child tests do that. It mutates only the `TEST` environment variable and current working directory while dispatching.

## Dependencies And Integration Points
It is the suite dispatcher for the per-directory keyctl tests and relies on each child script sourcing the preparation/toolbox files.

## Risks And Edge Cases
Whitespace in test paths is not handled. Non-automated mode returns on first failure, which is useful for debugging but can hide later failures.

## Test Signals
Signals are child exit status in interactive mode and the presence of per-test banners for automation logs.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/runtest.sh -->
