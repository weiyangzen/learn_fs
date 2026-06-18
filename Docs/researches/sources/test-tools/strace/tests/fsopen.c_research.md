<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fsopen.c -->
# sources/test-tools/strace/tests/fsopen.c

## Purpose
Covers strace decoder coverage for `fsopen`. Source comments describe: Check decoding of fsopen syscall. FSOPEN_??? FSOPEN_??? Source read: 59 lines, 1502 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <stdint.h>, <unistd.h>; defines: none; C functions: k_fsopen, main; syscall names/numbers: fsopen, __NR_fsopen.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. small syscall wrapper helpers OR high filler bits into integer arguments so strace's decoding and truncation paths are exercised. primary syscall coverage is fsopen, __NR_fsopen.

## State And Persistence Behavior
uses tail-allocated buffers to create valid, short-read, and EFAULT-adjacent pointer cases; opens descriptors, commonly `/dev/null`, `/dev/full`, or the current directory, for fd/path decoding.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fsopen.c -->
