<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/rt_sigprocmask.c -->
# sources/test-tools/strace/tests/rt_sigprocmask.c

## Purpose

`sources/test-tools/strace/tests/rt_sigprocmask.c` checks `rt_sigprocmask` action, old/new signal-set, and sigset-size decoding in the strace tests tree. Source read: complete file, 147 lines, 4235 bytes, sha256 `d9c0bc1cec5c7efc`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`, `<assert.h>`, `<signal.h>`, `<stdio.h>`, `<string.h>`, `<unistd.h>`. Compile-time macros: none found. Functions/helpers: `iterate`, `k_sigprocmask`, `main`. Direct syscall numbers: `__NR_rt_sigprocmask`. Notable constants/xlats: `SIGALRM`, `SIGHUP`, `SIGINT`, `SIGKILL`, `SIGQUIT`, `SIGTERM`, `SIG_BLOCK`, `SIG_SETMASK`, `SIG_UNBLOCK`.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes `__NR_rt_sigprocmask` directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `iterate`, `k_sigprocmask`, `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; kernel syscall availability for `__NR_rt_sigprocmask`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; signal timing and restart behavior must remain deterministic enough for golden-output comparison.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/rt_sigprocmask.c -->
