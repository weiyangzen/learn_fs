<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/inject-nf.c -->
# sources/test-tools/strace/tests/inject-nf.c

## Purpose
Covers strace decoder coverage for `return`. Source comments describe: Check decoding of return values injected into a syscall that "never fails". No raw_syscall_0, let's use geteuid() and hope for the best. This prototype is intentionally different from the prototype provided by <unistd.h>. Source read: 64 lines, 1357 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <assert.h>, <stdio.h>, <stdlib.h>, "scno.h", "raw_syscall.h"; defines: SC_NR, SC_NAME, INVOKE_SC; C functions: main; syscall names/numbers: geteuid32, geteuid.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. primary syscall coverage is geteuid32, geteuid.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: program stdout contains the canonical expected strace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/inject-nf.c -->
