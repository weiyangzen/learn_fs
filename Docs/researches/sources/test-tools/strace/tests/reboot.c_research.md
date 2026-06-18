<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/reboot.c -->
# sources/test-tools/strace/tests/reboot.c

## Purpose

`sources/test-tools/strace/tests/reboot.c` checks `reboot` magic, command, and argument decoding, including invalid magic/cmd fallback in the strace tests tree. Source read: complete file, 100 lines, 3515 bytes, sha256 `59691a65de166230`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`, `<stdio.h>`, `<linux/reboot.h>`, `<unistd.h>`. Compile-time macros: `INVALID_MAGIC`, `INVALID_CMD`, `STR32`, `STR128`. Functions/helpers: `main`. Direct syscall numbers: `__NR_reboot`. Notable constants/xlats: none found.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes `__NR_reboot` directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; kernel syscall availability for `__NR_reboot`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/reboot.c -->
