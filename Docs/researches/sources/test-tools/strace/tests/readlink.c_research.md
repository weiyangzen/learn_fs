<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/readlink.c -->
# sources/test-tools/strace/tests/readlink.c

## Purpose

`sources/test-tools/strace/tests/readlink.c` checks `readlink` path, buffer, and size decoding using direct syscall invocations in the strace tests tree. Source read: complete file, 62 lines, 1366 bytes, sha256 `471cd719b44f01cb`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`. Compile-time macros: none found. Functions/helpers: `main`. Direct syscall numbers: `__NR_readlink`. Notable constants/xlats: none found.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes `__NR_readlink` directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; kernel syscall availability for `__NR_readlink`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; path, fd, buffer, and invalid-pointer formatting are intentionally exercised and are easy to regress.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/readlink.c -->
