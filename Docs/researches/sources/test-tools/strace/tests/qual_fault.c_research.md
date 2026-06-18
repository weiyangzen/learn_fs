<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/qual_fault.c -->
# sources/test-tools/strace/tests/qual_fault.c

## Purpose

`sources/test-tools/strace/tests/qual_fault.c` checks strace fault injection across traced syscalls and child process behavior in the strace tests tree. Source read: complete file, 193 lines, 3925 bytes, sha256 `1f86fab06957454c`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `<assert.h>`, `<errno.h>`, `<fcntl.h>`, `<limits.h>`, `<stdio.h>`, `<stdlib.h>`, `<string.h>`, `<unistd.h>`, `<sys/stat.h>`, `<sys/uio.h>`, `<sys/wait.h>`. Compile-time macros: `DEFAULT_ERRNO`. Functions/helpers: `invoke`, `main`, `open_file`. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes the target libc/syscall wrapper directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `invoke`, `main`, `open_file` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/qual_fault.c -->
