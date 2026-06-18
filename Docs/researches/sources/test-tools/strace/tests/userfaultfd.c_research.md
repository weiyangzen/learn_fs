<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/userfaultfd.c -->
# sources/test-tools/strace/tests/userfaultfd.c

## Purpose
Covers strace decoder coverage for `userfaultfd`. Source comments/macros state: Check decoding of userfaultfd syscall. Source read: 59 lines, 1476 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>, "kernel_fcntl.h"; defines/undefs: UFFD_USER_MODE_ONLY; C functions: k_userfaultfd, main; syscall numbers/wrappers: userfaultfd, __NR_userfaultfd; struct types: strval32.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. loops enumerate flag, pointer, descriptor, pid, or xlat-mode combinations. primary syscall coverage: userfaultfd, __NR_userfaultfd.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; kernel configuration, procfs visibility, or privileges can change availability. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/userfaultfd.c -->
