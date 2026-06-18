<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/futex_waitv.c -->
# sources/test-tools/strace/tests/futex_waitv.c

## Purpose
Covers strace decoder coverage for `futex_waitv`. Source comments describe: Check decoding of futex_waitv syscall. CLOCK_??? %p Source read: 136 lines, 4439 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", "kernel_timespec.h", <stdio.h>, <stdlib.h>, <time.h>, <unistd.h>, <linux/futex.h>; defines: none; C functions: k_futex_waitv, main; syscall names/numbers: futex_waitv, __NR_futex_waitv; struct types: futex_waitv.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. small syscall wrapper helpers OR high filler bits into integer arguments so strace's decoding and truncation paths are exercised. nested loops cover flag, pointer, size, fd, and translation-mode combinations. primary syscall coverage is futex_waitv, __NR_futex_waitv.

## State And Persistence Behavior
uses tail-allocated buffers to create valid, short-read, and EFAULT-adjacent pointer cases.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, `kernel_timespec.h`, Linux UAPI headers, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/futex_waitv.c -->
