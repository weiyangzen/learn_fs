<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/run.sh -->
# sources/test-tools/strace/tests/run.sh

## Purpose

`sources/test-tools/strace/tests/run.sh` is the common shell launcher that verifies strace availability, configures timeout, and execs a test command in the strace tests tree. Source read: complete file, 22 lines, 435 bytes, sha256 `9e2388f8d9a299fd`.

## Important APIs, Types, and Functions

Includes: none found. Compile-time macros: none found. Functions/helpers: none found. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

The script sources `init.sh`, checks that `$STRACE -V` works, configures a timeout command when available, validates that a command was supplied, and `exec`s the test command with stdin redirected from `/dev/null`.

## State and Persistence Behavior

No durable application state is owned here. Temporary harness files such as `$LOG`, `$OUT`, `$EXP`, process exit statuses, and environment variables carry state only for the current test run.

## Dependencies and Integration Points

the shell harness from `init.sh`, `$STRACE`, and generated `$LOG`/`$OUT`/`$EXP` files. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

Risks include architecture/personality detection drift, missing helper commands, environment-variable assumptions, and fragile skip/fail behavior under cross-architecture test runs.

## Test Signals

Test signals are explicit `skip_`/`fail_` paths, `match_diff`/`match_grep` comparisons, and successful execution under the architecture/personality matrix.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/run.sh -->
