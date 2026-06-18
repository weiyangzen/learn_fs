<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ptrace_syscall_info.c -->
# sources/test-tools/strace/tests/ptrace_syscall_info.c

## Purpose

This test verifies strace decoding of `PTRACE_GET_SYSCALL_INFO` across none, syscall-entry, and syscall-exit stops. Source read: complete file, 473 lines, 12790 bytes, sha256 `1a683c8010a65328`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"ptrace.h"`, `"scno.h"`, `<errno.h>`, `<stddef.h>`, `<stdio.h>`, `<string.h>`, `<signal.h>`, `<sys/wait.h>`, `<unistd.h>`, `<linux/audit.h>`, `"xlat.h"`, `"xlat/audit_arch.h"`. Compile-time macros: `XLAT_MACROS_ONLY`, `FAIL`, `PFAIL`. Functions/helpers: `do_ptrace`, `kill_tracee`, `main`, `test_entry`, `test_exit`, `test_none`. Direct syscall numbers: `__NR_chdir`, `__NR_exit_group`, `__NR_gettid`, `__NR_ptrace`. Notable constants/xlats: `AUDIT_ARCH_`, `PTRACE_GET_SYSCALL_INFO`, `PTRACE_O_TRACESYSGOOD`, `PTRACE_SETOPTIONS`, `PTRACE_SYSCALL`, `PTRACE_SYSCALL_INFO_ENTRY`, `PTRACE_SYSCALL_INFO_EXIT`, `PTRACE_SYSCALL_INFO_NONE`, `PTRACE_TRACEME`, `SIGKILL`, `SIGSTOP`, `SIGTRAP`.

## Control Flow

It forks a tracee, enables `PTRACE_O_TRACESYSGOOD`, steps through `chdir`, `gettid`, and `exit_group` with `PTRACE_SYSCALL`, and for every stop reads `struct_ptrace_syscall_info` with sizes from 0 through the full struct size. The expected line printer checks op, audit arch, instruction and stack pointers, syscall numbers, argument arrays, return values, and `is_error`.

## State and Persistence Behavior

State is process-local: tracee pid, wait status, ptrace stop counter, tail-allocated buffers, and `errstr` from the latest syscall. No durable state is written.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; generated xlat tables and xlat formatting macros; kernel syscall availability for `__NR_chdir`, `__NR_exit_group`, `__NR_gettid`, `__NR_ptrace`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

Kernel support for `PTRACE_GET_SYSCALL_INFO`, syscall-stop sequencing, audit-arch values, and struct-size changes are the key compatibility risks.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable; ptrace stop sequencing and partial-buffer field cutoffs.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ptrace_syscall_info.c -->
