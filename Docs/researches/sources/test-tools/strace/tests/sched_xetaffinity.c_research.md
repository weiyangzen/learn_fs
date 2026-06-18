<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sched_xetaffinity.c -->
# sources/test-tools/strace/tests/sched_xetaffinity.c

## Purpose

`sources/test-tools/strace/tests/sched_xetaffinity.c` checks `sched_getaffinity` and `sched_setaffinity` cpuset-size and mask decoding in the strace tests tree. Source read: complete file, 155 lines, 4401 bytes, sha256 `32ee58964b01a9e5`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`, `"pidns.h"`, `<sched.h>`. Compile-time macros: none found. Functions/helpers: `getaffinity`, `main`, `setaffinity`. Direct syscall numbers: `__NR_sched_getaffinity`, `__NR_sched_setaffinity`. Notable constants/xlats: none found.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes `__NR_sched_getaffinity`, `__NR_sched_setaffinity` directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `getaffinity`, `main`, `setaffinity` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; pid namespace translation helpers; kernel syscall availability for `__NR_sched_getaffinity`, `__NR_sched_setaffinity`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sched_xetaffinity.c -->
