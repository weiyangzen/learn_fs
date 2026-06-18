<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/rseq.c -->
# sources/test-tools/strace/tests/rseq.c

## Purpose

`sources/test-tools/strace/tests/rseq.c` checks `rseq` syscall decoding for registration pointers, lengths, flags, and signatures in the strace tests tree. Source read: complete file, 175 lines, 5883 bytes, sha256 `88c588b56c2433e1`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`, `<stdio.h>`, `<string.h>`, `<unistd.h>`, `<linux/rseq.h>`. Compile-time macros: none found. Functions/helpers: `k_rseq`, `main`. Direct syscall numbers: `__NR_rseq`. Notable constants/xlats: `RSEQ_CPU_ID_REGISTRATION_FAILED`, `RSEQ_CPU_ID_UNINITIALIZED`, `RSEQ_CS_FLAG_`, `RSEQ_CS_FLAG_NO_RESTART_ON_MIGRATE`, `RSEQ_CS_FLAG_NO_RESTART_ON_PREEMPT`, `RSEQ_CS_FLAG_NO_RESTART_ON_SIGNAL`, `RSEQ_CS_FLAG_SLICE_EXT_AVAILABLE`, `RSEQ_CS_FLAG_SLICE_EXT_ENABLED`, `RSEQ_FLAG_`, `RSEQ_FLAG_SLICE_EXT_DEFAULT_ON`, `RSEQ_FLAG_UNREGISTER`, `RSEQ_TEST_ALIGN`, `RSEQ_TEST_MIN`.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes `__NR_rseq` directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `k_rseq`, `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; kernel syscall availability for `__NR_rseq`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/rseq.c -->
