<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/quotactl-success-v.c -->
# sources/test-tools/strace/tests/quotactl-success-v.c

## Purpose

This is a thin compile-time wrapper around `quotactl-v.c`. Its local purpose is to rebuild the shared test body in success-injection mode, usually forcing a synthetic successful return value. Source read: complete file, 2 lines, 49 bytes, sha256 `fad8685117b78987`.

## Important APIs, Types, and Functions

Includes: `"quotactl-v.c"`. Compile-time macros: `INJECT_RETVAL`. Functions/helpers: none found. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

Preprocessing defines `INJECT_RETVAL` and then includes `quotactl-v.c`. The included body supplies `main` and all syscall-driving logic; this file changes only the expected rendering mode or skip prerequisite.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

the surrounding strace tests build and harness rules. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

The main risk is divergence between the wrapper macro and the shared test body's expected output; a change in the included file affects this variant without local code changing.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable; syscall retval injection producing the synthetic success path.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/quotactl-success-v.c -->
