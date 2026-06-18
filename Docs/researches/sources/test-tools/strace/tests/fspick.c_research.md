<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fspick.c -->
# sources/test-tools/strace/tests/fspick.c

## Purpose
Covers strace decoder coverage for `fspick`. Source comments describe: Check decoding of fspick syscall. FSPICK_??? Source read: 104 lines, 2720 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <fcntl.h>, <limits.h>, <stdio.h>, <stdint.h>, <unistd.h>; defines: none; C functions: k_fspick, main; syscall names/numbers: fspick, __NR_fspick.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. small syscall wrapper helpers OR high filler bits into integer arguments so strace's decoding and truncation paths are exercised. primary syscall coverage is fspick, __NR_fspick.

## State And Persistence Behavior
uses tail-allocated buffers to create valid, short-read, and EFAULT-adjacent pointer cases; opens descriptors, commonly `/dev/null`, `/dev/full`, or the current directory, for fd/path decoding.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability, `/proc/self/fd`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling; path-decoding variants require procfs fd links. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared; skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fspick.c -->
