<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/recv-MSG_TRUNC.c -->
# sources/test-tools/strace/tests/recv-MSG_TRUNC.c

## Purpose

`sources/test-tools/strace/tests/recv-MSG_TRUNC.c` checks `recv` behavior and output formatting when `MSG_TRUNC` is involved in the strace tests tree. Source read: complete file, 59 lines, 1391 bytes, sha256 `66102600c342fc04`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `<errno.h>`, `<stdio.h>`, `<sys/socket.h>`, `"scno.h"`. Compile-time macros: `SC_recv`. Functions/helpers: `main`, `sys_recv`. Direct syscall numbers: `__NR_recv`. Notable constants/xlats: `MSG_PEEK`, `MSG_TRUNC`.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes `__NR_recv` directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `main`, `sys_recv` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; kernel syscall availability for `__NR_recv`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; path, fd, buffer, and invalid-pointer formatting are intentionally exercised and are easy to regress.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/recv-MSG_TRUNC.c -->
