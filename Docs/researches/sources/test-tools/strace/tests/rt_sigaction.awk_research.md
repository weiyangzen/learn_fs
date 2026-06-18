<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/rt_sigaction.awk -->
# sources/test-tools/strace/tests/rt_sigaction.awk

## Purpose

`sources/test-tools/strace/tests/rt_sigaction.awk` is the awk postprocessor/generator used by rt_sigaction tests to normalize architecture-specific signal-action traces in the strace tests tree. Source read: complete file, 76 lines, 2114 bytes, sha256 `3d462e72d55de31a`.

## Important APIs, Types, and Functions

Includes: none found. Compile-time macros: none found. Functions/helpers: none found. Direct syscall numbers: none found. Notable constants/xlats: `SIGRT`, `SIGUSR2`, `SIG_DFL`, `SIG_IGN`.

## Control Flow

The awk program reads trace lines, applies regular-expression matching and field rewriting, and emits normalized expected output suitable for architecture-independent comparison.

## State and Persistence Behavior

No durable application state is owned here. Temporary harness files such as `$LOG`, `$OUT`, `$EXP`, process exit statuses, and environment variables carry state only for the current test run.

## Dependencies and Integration Points

GNU awk-compatible regex and text-processing behavior. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

Risks include regexes that are too broad or too narrow, architecture-specific signal-action formatting changes, and awk portability assumptions.

## Test Signals

Test signals are stable normalized output from representative rt_sigaction traces and successful comparison by the surrounding test.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/rt_sigaction.awk -->
