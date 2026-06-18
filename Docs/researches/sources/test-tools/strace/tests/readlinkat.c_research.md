<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/readlinkat.c -->
# sources/test-tools/strace/tests/readlinkat.c

## Purpose

`sources/test-tools/strace/tests/readlinkat.c` checks `readlinkat` path, dirfd, buffer, and size decoding with a generated symlink fixture in the strace tests tree. Source read: complete file, 56 lines, 1374 bytes, sha256 `677d94a5b79b7252`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`, `<stdio.h>`, `<unistd.h>`. Compile-time macros: `PREFIX`, `TARGET`, `LINKPATH`. Functions/helpers: `main`. Direct syscall numbers: `__NR_readlinkat`. Notable constants/xlats: `AT_FDCWD`.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes `__NR_readlinkat` directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

The test creates/removes temporary pathnames for a target and symlink, but it does not persist data beyond the harness run.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; kernel syscall availability for `__NR_readlinkat`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; path, fd, buffer, and invalid-pointer formatting are intentionally exercised and are easy to regress.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/readlinkat.c -->
