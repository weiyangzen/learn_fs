<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getgroups.c -->
# sources/test-tools/strace/tests/getgroups.c

## Purpose
Covers strace decoder coverage for `getgroups`. Source comments describe: Check decoding of getgroups/getgroups32 syscalls. __NR_getgroups check how the first argument is decoded check how the second argument is decoded Source read: 104 lines, 2517 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>; defines: SYSCALL_NR, SYSCALL_NAME, GID_TYPE, MAX_STRLEN; C functions: get_groups, main; syscall names/numbers: getgroups32, getgroups, SYSCALL_NR.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. nested loops cover flag, pointer, size, fd, and translation-mode combinations. primary syscall coverage is getgroups32, getgroups, SYSCALL_NR.

## State And Persistence Behavior
uses tail-allocated buffers to create valid, short-read, and EFAULT-adjacent pointer cases.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getgroups.c -->
