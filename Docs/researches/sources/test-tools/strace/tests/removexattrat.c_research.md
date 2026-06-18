<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/removexattrat.c -->
# sources/test-tools/strace/tests/removexattrat.c

## Purpose

`sources/test-tools/strace/tests/removexattrat.c` checks `removexattrat` syscall decoding for fd/path, xattr name, and flag values in the strace tests tree. Source read: complete file, 150 lines, 3559 bytes, sha256 `1ad4157a2627bcc1`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`, `"xmalloc.h"`, `<fcntl.h>`, `<stdio.h>`, `<unistd.h>`, `<linux/xattr.h>`. Compile-time macros: `XLAT_MACROS_ONLY`. Functions/helpers: `k_removexattrat`, `main`. Direct syscall numbers: `__NR_removexattrat`. Notable constants/xlats: `AT_`, `AT_EMPTY_PATH`, `AT_FDCWD`, `AT_SYMLINK_NOFOLLOW`.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes `__NR_removexattrat` directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `k_removexattrat`, `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; kernel syscall availability for `__NR_removexattrat`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; path, fd, buffer, and invalid-pointer formatting are intentionally exercised and are easy to regress.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/removexattrat.c -->
