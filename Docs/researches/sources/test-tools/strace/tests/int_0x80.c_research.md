<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/int_0x80.c -->
# sources/test-tools/strace/tests/int_0x80.c

## Purpose
Covers strace decoder coverage for `int`. Source comments describe: Check decoding of int 0x80 on x86_64, x32, and x86. 200 is __NR_getgid32 on x86 and __NR_tkill on x86_64. Source read: 32 lines, 570 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <stdio.h>, <unistd.h>; defines: none; C functions: main; syscall names/numbers: getgid32, tkill.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. primary syscall coverage is getgid32, tkill.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: program stdout contains the canonical expected strace lines; skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/int_0x80.c -->
