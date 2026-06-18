<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ptrace_syscall_info-Xraw.c -->
# sources/test-tools/strace/tests/ptrace_syscall_info-Xraw.c

## Purpose

This is a thin compile-time wrapper around `ptrace_syscall_info.c`. Its local purpose is to rebuild the shared test body in raw xlat mode, so symbolic constants are expected as numeric values where the shared body uses xlat formatting. Source read: complete file, 2 lines, 52 bytes, sha256 `345fa34ccaf99349`.

## Important APIs, Types, and Functions

Includes: `"ptrace_syscall_info.c"`. Compile-time macros: `XLAT_RAW`. Functions/helpers: none found. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

Preprocessing defines `XLAT_RAW` and then includes `ptrace_syscall_info.c`. The included body supplies `main` and all syscall-driving logic; this file changes only the expected rendering mode or skip prerequisite.

## State and Persistence Behavior

State is process-local: tracee pid, wait status, ptrace stop counter, tail-allocated buffers, and `errstr` from the latest syscall. No durable state is written.

## Dependencies and Integration Points

the surrounding strace tests build and harness rules. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

The main risk is divergence between the wrapper macro and the shared test body's expected output; a change in the included file affects this variant without local code changing.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable; coverage of the selected xlat rendering mode.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ptrace_syscall_info-Xraw.c -->
