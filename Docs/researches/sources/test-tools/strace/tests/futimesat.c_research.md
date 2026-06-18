<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/futimesat.c -->
# sources/test-tools/strace/tests/futimesat.c

## Purpose
Covers strace decoder coverage for `futimesat`. Source comments describe: Check decoding of futimesat syscall. dirfd pathname times Source read: 148 lines, 3842 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", "kernel_timeval.h", <stdint.h>, <stdio.h>, <sys/time.h>, <unistd.h>; defines: none; C functions: print_tv, k_futimesat, main; syscall names/numbers: futimesat, __NR_futimesat.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. small syscall wrapper helpers OR high filler bits into integer arguments so strace's decoding and truncation paths are exercised. primary syscall coverage is futimesat, __NR_futimesat.

## State And Persistence Behavior
uses tail-allocated buffers to create valid, short-read, and EFAULT-adjacent pointer cases.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, `kernel_timeval.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared; skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/futimesat.c -->
