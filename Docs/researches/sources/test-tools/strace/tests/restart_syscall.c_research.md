<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/restart_syscall.c -->
# sources/test-tools/strace/tests/restart_syscall.c

## Purpose

`sources/test-tools/strace/tests/restart_syscall.c` checks interrupted nanosleep restart tracing and restart-syscall rendering in the strace tests tree. Source read: complete file, 69 lines, 2103 bytes, sha256 `d2fe8abfcb04b790`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `<stdio.h>`, `<stdint.h>`, `<signal.h>`, `<time.h>`, `<sys/time.h>`. Compile-time macros: `NANOSLEEP_NAME_RE`, `NANOSLEEP_CALL_RE`. Functions/helpers: `main`. Direct syscall numbers: none found. Notable constants/xlats: `SIGALRM`, `SIG_IGN`, `SIG_SETMASK`.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes the target libc/syscall wrapper directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; signal timing and restart behavior must remain deterministic enough for golden-output comparison.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/restart_syscall.c -->
