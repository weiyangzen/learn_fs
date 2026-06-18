<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/rt_sigreturn.c -->
# sources/test-tools/strace/tests/rt_sigreturn.c

## Purpose

`sources/test-tools/strace/tests/rt_sigreturn.c` checks sigreturn/rt_sigreturn tracing around an actual signal handler in the strace tests tree. Source read: complete file, 59 lines, 1299 bytes, sha256 `15171691bf5d4b52`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `<signal.h>`, `<stdio.h>`, `<stdlib.h>`. Compile-time macros: none found. Functions/helpers: `handler`, `main`. Direct syscall numbers: none found. Notable constants/xlats: `RT_0`, `RT_26`, `RT_27`, `RT_3`, `RT_4`, `RT_5`, `SIGCHLD`, `SIGINT`, `SIGRTMIN`, `SIGUSR1`, `SIGUSR2`, `SIG_SETMASK`.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes the target libc/syscall wrapper directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `handler`, `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; signal timing and restart behavior must remain deterministic enough for golden-output comparison.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/rt_sigreturn.c -->
