<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/rt_sigsuspend.c -->
# sources/test-tools/strace/tests/rt_sigsuspend.c

## Purpose

`sources/test-tools/strace/tests/rt_sigsuspend.c` checks `rt_sigsuspend` syscall decoding and interrupted-signal behavior in the strace tests tree. Source read: complete file, 136 lines, 3440 bytes, sha256 `8bf972cc075b1343`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`, `<assert.h>`, `<errno.h>`, `<signal.h>`, `<stdio.h>`, `<stdint.h>`, `<string.h>`, `<unistd.h>`. Compile-time macros: none found. Functions/helpers: `handler`, `iterate`, `k_sigsuspend`, `main`. Direct syscall numbers: `__NR_rt_sigsuspend`. Notable constants/xlats: `SIGHUP`, `SIGINT`, `SIGUSR1`, `SIGUSR2`, `SIG_SETMASK`.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes `__NR_rt_sigsuspend` directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `handler`, `iterate`, `k_sigsuspend`, `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; kernel syscall availability for `__NR_rt_sigsuspend`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; signal timing and restart behavior must remain deterministic enough for golden-output comparison.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/rt_sigsuspend.c -->
