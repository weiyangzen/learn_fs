<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/s390_runtime_instr.c -->
# sources/test-tools/strace/tests/s390_runtime_instr.c

## Purpose

`sources/test-tools/strace/tests/s390_runtime_instr.c` checks s390 runtime instrumentation syscall command and signum formatting in the strace tests tree. Source read: complete file, 77 lines, 1648 bytes, sha256 `94437b6b9dd3e71b`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`. Compile-time macros: none found. Functions/helpers: `main`. Direct syscall numbers: `__NR_s390_runtime_instr`. Notable constants/xlats: `S390_RUNTIME_INSTR_`, `S390_RUNTIME_INSTR_START`, `S390_RUNTIME_INSTR_STOP`, `SIGALRM`, `SIGRT_1`, `SIGRT_31`.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes `__NR_s390_runtime_instr` directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; kernel syscall availability for `__NR_s390_runtime_instr`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; the test may be skipped or behave differently outside its target architecture.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/s390_runtime_instr.c -->
