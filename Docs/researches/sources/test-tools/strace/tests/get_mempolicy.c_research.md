<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/get_mempolicy.c -->
# sources/test-tools/strace/tests/get_mempolicy.c

## Purpose
Covers strace decoder coverage for `get_mempolicy`. Source comments describe: Check decoding of get_mempolicy syscall. Source read: 105 lines, 2729 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>, "xlat.h", "xlat/mpol_modes.h"; defines: MAX_STRLEN, NLONGS; C functions: print_nodes, main; syscall names/numbers: get_mempolicy, __NR_get_mempolicy.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. nested loops cover flag, pointer, size, fd, and translation-mode combinations. primary syscall coverage is get_mempolicy, __NR_get_mempolicy.

## State And Persistence Behavior
uses tail-allocated buffers to create valid, short-read, and EFAULT-adjacent pointer cases.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, `xlat.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/get_mempolicy.c -->
