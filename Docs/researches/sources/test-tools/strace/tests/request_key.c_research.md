<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/request_key.c -->
# sources/test-tools/strace/tests/request_key.c

## Purpose

`sources/test-tools/strace/tests/request_key.c` checks `request_key` syscall decoding for key type, description, callout info, and destination keyring in the strace tests tree. Source read: complete file, 119 lines, 2885 bytes, sha256 `1484c11dd4456169`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`, `<inttypes.h>`, `<stdio.h>`, `<unistd.h>`. Compile-time macros: none found. Functions/helpers: `do_request_key`, `main`, `print_val_str`. Direct syscall numbers: `__NR_request_key`. Notable constants/xlats: `KEY_SPEC_THREAD_KEYRING`.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes `__NR_request_key` directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `do_request_key`, `main`, `print_val_str` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; kernel syscall availability for `__NR_request_key`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/request_key.c -->
