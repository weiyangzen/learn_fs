<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/redirect-fds.c -->
# sources/test-tools/strace/tests/redirect-fds.c

## Purpose

`sources/test-tools/strace/tests/redirect-fds.c` checks test-harness fd redirection expectations for stdin/stdout/stderr-style descriptors in the strace tests tree. Source read: complete file, 54 lines, 894 bytes, sha256 `2397a3ac3b921dfe`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `<assert.h>`, `<unistd.h>`, `<sys/stat.h>`. Compile-time macros: `N_FDS`. Functions/helpers: `check_fd`, `main`. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes the target libc/syscall wrapper directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `check_fd`, `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to process file descriptors, temporary pathnames, and syscall return/errno values generated during the test.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/redirect-fds.c -->
