<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/recvfrom-MSG_TRUNC.c -->
# sources/test-tools/strace/tests/recvfrom-MSG_TRUNC.c

## Purpose

`sources/test-tools/strace/tests/recvfrom-MSG_TRUNC.c` checks `recvfrom` buffer and sockaddr output with `MSG_TRUNC` in the strace tests tree. Source read: complete file, 42 lines, 1145 bytes, sha256 `29b4aef83fdb02dc`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `<stdio.h>`, `<sys/socket.h>`. Compile-time macros: none found. Functions/helpers: `main`. Direct syscall numbers: none found. Notable constants/xlats: `MSG_PEEK`, `MSG_TRUNC`.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes the target libc/syscall wrapper directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; path, fd, buffer, and invalid-pointer formatting are intentionally exercised and are easy to regress.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/recvfrom-MSG_TRUNC.c -->
