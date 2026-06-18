<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/rt_sigpending.c -->
# sources/test-tools/strace/tests/rt_sigpending.c

## Purpose

`sources/test-tools/strace/tests/rt_sigpending.c` checks `rt_sigpending` syscall decoding for signal-set buffers and sigset sizes in the strace tests tree. Source read: complete file, 101 lines, 2245 bytes, sha256 `0a14fde86ea58f25`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`, `<assert.h>`, `<signal.h>`, `<stdio.h>`, `<string.h>`, `<unistd.h>`. Compile-time macros: none found. Functions/helpers: `iterate`, `k_sigpending`, `main`. Direct syscall numbers: `__NR_rt_sigpending`. Notable constants/xlats: `SIGHUP`, `SIGINT`, `SIG_SETMASK`.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes `__NR_rt_sigpending` directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `iterate`, `k_sigpending`, `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; kernel syscall availability for `__NR_rt_sigpending`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; signal timing and restart behavior must remain deterministic enough for golden-output comparison.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/rt_sigpending.c -->
