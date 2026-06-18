<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/s390_guarded_storage.c -->
# sources/test-tools/strace/tests/s390_guarded_storage.c

## Purpose

`sources/test-tools/strace/tests/s390_guarded_storage.c` checks s390 `s390_guarded_storage` syscall decoding for control-block and event-parameter-list forms in the strace tests tree. Source read: complete file, 208 lines, 5240 bytes, sha256 `e76b2969b5a9f4ba`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`. Compile-time macros: none found. Functions/helpers: `gs_no_arg`, `gs_print_epl`, `gs_set_cb`, `main`. Direct syscall numbers: `__NR_s390_guarded_storage`. Notable constants/xlats: none found.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes `__NR_s390_guarded_storage` directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `gs_no_arg`, `gs_print_epl`, `gs_set_cb`, `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; kernel syscall availability for `__NR_s390_guarded_storage`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; the test may be skipped or behave differently outside its target architecture.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/s390_guarded_storage.c -->
