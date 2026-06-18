<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/removexattrat-y.c -->
# sources/test-tools/strace/tests/removexattrat-y.c

## Purpose

This is a thin compile-time wrapper around `removexattrat.c`. Its local purpose is to rebuild the shared test body in default mode with no local behavior override. Source read: complete file, 4 lines, 132 bytes, sha256 `29779aef16c298b8`.

## Important APIs, Types, and Functions

Includes: `"removexattrat.c"`. Compile-time macros: `FD_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`. Functions/helpers: none found. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

Preprocessing defines `FD_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE` and then includes `removexattrat.c`. The included body supplies `main` and all syscall-driving logic; this file changes only the expected rendering mode or skip prerequisite.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

the surrounding strace tests build and harness rules. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

The main risk is divergence between the wrapper macro and the shared test body's expected output; a change in the included file affects this variant without local code changing.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/removexattrat-y.c -->
