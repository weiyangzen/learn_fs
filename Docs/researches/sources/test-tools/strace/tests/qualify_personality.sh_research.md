<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/qualify_personality.sh -->
# sources/test-tools/strace/tests/qualify_personality.sh

## Purpose

`sources/test-tools/strace/tests/qualify_personality.sh` is shared shell logic for per-personality `-e trace=...@personality` tests in the strace tests tree. Source read: complete file, 52 lines, 1157 bytes, sha256 `d6969d709264cba3`.

## Important APIs, Types, and Functions

Includes: none found. Compile-time macros: none found. Functions/helpers: none found. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

The script sources `init.sh`, validates a requested personality designator, computes supported personalities from `STRACE_NATIVE_ARCH`, resets `NAME` to an empty fixture for non-current personalities, and calls `test_trace_expr` with `trace_expr@personality`.

## State and Persistence Behavior

No durable application state is owned here. Temporary harness files such as `$LOG`, `$OUT`, `$EXP`, process exit statuses, and environment variables carry state only for the current test run.

## Dependencies and Integration Points

the shell harness from `init.sh`, `$STRACE`, and generated `$LOG`/`$OUT`/`$EXP` files. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

Risks include architecture/personality detection drift, missing helper commands, environment-variable assumptions, and fragile skip/fail behavior under cross-architecture test runs.

## Test Signals

Test signals are explicit `skip_`/`fail_` paths, `match_diff`/`match_grep` comparisons, and successful execution under the architecture/personality matrix.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/qualify_personality.sh -->
