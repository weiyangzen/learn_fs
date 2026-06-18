<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ptrace_set_syscall_info.c -->
# sources/test-tools/strace/tests/ptrace_set_syscall_info.c

## Purpose

This test verifies strace decoding of the `PTRACE_SET_SYSCALL_INFO` request, including deliberately partial user buffers. Source read: complete file, 318 lines, 8429 bytes, sha256 `2479444aed6df008`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"ptrace.h"`, `"scno.h"`, `<errno.h>`, `<stddef.h>`, `<stdio.h>`, `<string.h>`, `<signal.h>`, `<sys/wait.h>`, `<unistd.h>`, `<linux/audit.h>`, `"cur_audit_arch.h"`, `"xlat.h"`. Compile-time macros: `XLAT_MACROS_ONLY`, `OOB`, `OOE`. Functions/helpers: `main`, `ptrace_set_syscall_info`, `test_entry`, `test_exit`, `test_none`. Direct syscall numbers: `__NR_gettid`, `__NR_ptrace`. Notable constants/xlats: `AUDIT_ARCH_`, `AUDIT_ARCH_CRIS`, `PTRACE_SET_SYSCALL_INFO`, `PTRACE_SYSCALL_INFO_`, `PTRACE_SYSCALL_INFO_ENTRY`, `PTRACE_SYSCALL_INFO_EXIT`, `PTRACE_SYSCALL_INFO_NONE`, `PTRACE_SYSCALL_INFO_SECCOMP`.

## Control Flow

It allocates a tail-page buffer, fills `struct_ptrace_syscall_info` with known bytes, then loops over buffer sizes and value tables for op, audit arch, syscall numbers, seccomp ret data, and exit status. Each call prints the expected decoded form for present fields only.

## State and Persistence Behavior

State is process-local: tracee pid, wait status, ptrace stop counter, tail-allocated buffers, and `errstr` from the latest syscall. No durable state is written.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; generated xlat tables and xlat formatting macros; kernel syscall availability for `__NR_gettid`, `__NR_ptrace`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

The test is sensitive to `struct_ptrace_syscall_info` layout, xlat rendering mode, and kernel availability of the synthetic ptrace request.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable; ptrace stop sequencing and partial-buffer field cutoffs.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ptrace_set_syscall_info.c -->
