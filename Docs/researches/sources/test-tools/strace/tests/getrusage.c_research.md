<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getrusage.c -->
# sources/test-tools/strace/tests/getrusage.c

## Purpose
Covers strace decoder coverage for `getrusage`. Source comments describe: Check decoding of getrusage syscall. Source read: 73 lines, 2389 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <stdint.h>, <sys/resource.h>, <unistd.h>, <errno.h>, "kernel_rusage.h", "xlat.h", "xlat/usagewho.h"; defines: none; C functions: invoke_print, main; syscall names/numbers: getrusage, __NR_getrusage.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. primary syscall coverage is getrusage, __NR_getrusage.

## State And Persistence Behavior
uses tail-allocated buffers to create valid, short-read, and EFAULT-adjacent pointer cases.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, `xlat.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getrusage.c -->
