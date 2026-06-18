<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ptrace.c -->
# sources/test-tools/strace/tests/ptrace.c

## Purpose

This is the broad ptrace decoder exerciser. It drives `__NR_ptrace` through request/value combinations including register access, regset access, signal-info decoding, peeksiginfo, compat request handling, and architecture-specific ptrace requests so strace output can be compared against the test program's generated expectations. Source read: complete file, 2335 lines, 67297 bytes, sha256 `04e1138214c9f3be`.

## Important APIs, Types, and Functions

Includes: `"tests.h"`, `"scno.h"`, `"print_fields.h"`, `<errno.h>`, `"ptrace.h"`, `<inttypes.h>`, `<fcntl.h>`, `<signal.h>`, `<stdint.h>`, `<stdio.h>`, `<string.h>`, `<sys/wait.h>`, `<unistd.h>`, `<linux/audit.h>`. Compile-time macros: `XLAT_MACROS_ONLY`, `NULL_FD`, `NULL_STR`. Functions/helpers: `check_compat_ptrace_req`, `do_getfpregs_setfpregs`, `do_getregs64_setregs64`, `do_getregs_setregs`, `do_getregset_setregset`, `do_ptrace`, `do_ptrace_regs`, `main`, `print_fpregset`, `print_prstatus_regset`, `print_pt_fpregs`, `print_pt_regs`, `print_pt_regs64`, `test_compat_ptrace`, `test_getregset_setregset`, `test_peeksiginfo`. Direct syscall numbers: `__NR_gettid`, `__NR_ptrace`, `__NR_read`. Notable constants/xlats: `AUDIT_ARCH_`, `AUDIT_ARCH_X86_64`, `PTRACE_`, `PTRACE_ATTACH`, `PTRACE_CONT`, `PTRACE_DETACH`, `PTRACE_GETEVENTMSG`, `PTRACE_GETFPREGS`, `PTRACE_GETREGS`, `PTRACE_GETREGS64`, `PTRACE_GETREGSET`, `PTRACE_GETSIGINFO`, `PTRACE_GETSIGMASK`, `PTRACE_INTERRUPT`, `PTRACE_KILL`, `PTRACE_LISTEN`, `PTRACE_O_TRACECLONE`, `PTRACE_O_TRACEFORK`, `PTRACE_O_TRACESYSGOOD`, `PTRACE_PEEKDATA`.

## Control Flow

The test first probes simple invalid/current-process ptrace calls, then forks a tracee, coordinates `PTRACE_TRACEME`, signal stops, `waitpid`, and ptrace request execution. Helper families print expected request names, pointer arguments, register structs, `iovec`/regset content, `siginfo_t` fields, and errno strings. Large conditional blocks compile only when the architecture exposes the corresponding ptrace structures or constants.

## State and Persistence Behavior

State is process-local: tracee pid, wait status, ptrace stop counter, tail-allocated buffers, and `errstr` from the latest syscall. No durable state is written.

## Dependencies and Integration Points

strace `tests.h` helpers for skip/fail/reporting, tail allocation, memory filling, and expected-result formatting; `scno.h` syscall-number indirection for portable direct syscall calls; generated xlat tables and xlat formatting macros; kernel syscall availability for `__NR_gettid`, `__NR_ptrace`, `__NR_read`. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

The main risks are architecture drift in register layouts, optional `siginfo_t` fields, ptrace request availability, and kernel behavior differences around compat tracing. The test intentionally uses invalid addresses and request numbers, so expected output must distinguish decoder fallback from syscall failure.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable; ptrace stop sequencing and partial-buffer field cutoffs.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ptrace.c -->
