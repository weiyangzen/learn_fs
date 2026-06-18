<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/qual_inject-error-signal.c -->
# sources/test-tools/strace/tests/qual_inject-error-signal.c

## Purpose

`sources/test-tools/strace/tests/qual_inject-error-signal.c` checks combined errno and signal injection qualification in the strace tests tree. Source read: complete file, 50 lines, 1025 bytes, sha256 `dfbbde1ab64f28ec`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `<signal.h>`, `<unistd.h>`, `<sys/stat.h>`, `"scno.h"`. Compile-time macros: none found. Functions/helpers: `handler`, `main`. Direct syscall numbers: `__NR_chdir`, `__NR_exit_group`. Notable constants/xlats: `SIGUSR1`, `SIG_UNBLOCK`.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes `__NR_chdir`, `__NR_exit_group` directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `handler`, `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; kernel syscall availability for `__NR_chdir`, `__NR_exit_group`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; signal timing and restart behavior must remain deterministic enough for golden-output comparison.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/qual_inject-error-signal.c -->
