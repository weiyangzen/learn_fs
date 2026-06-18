<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/pwritev.c -->
# sources/test-tools/strace/tests/pwritev.c

## Purpose

`sources/test-tools/strace/tests/pwritev.c` validates `pwritev` iovec and offset decoding, including multiple vector entries and invalid pointer handling in the strace tests tree. Source read: complete file, 131 lines, 2737 bytes, sha256 `05c80f422ccbb921`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`. Compile-time macros: none found. Functions/helpers: `main`, `print_iov`, `print_iovec`. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes the target libc/syscall wrapper directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `main`, `print_iov`, `print_iovec` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; path, fd, buffer, and invalid-pointer formatting are intentionally exercised and are easy to regress.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/pwritev.c -->
