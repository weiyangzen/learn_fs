<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/unshare.c -->
# sources/test-tools/strace/tests/unshare.c

## Purpose
Covers strace decoder coverage for `unshare`. Source comments/macros state: Check decoding of unshare syscall. CLONE_??? CLONE_??? Source read: 93 lines, 2430 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <limits.h>, <stdio.h>, <unistd.h>; defines/undefs: LINE_END; C functions: main; syscall numbers/wrappers: unshare, __NR_unshare.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. loops enumerate flag, pointer, descriptor, pid, or xlat-mode combinations. primary syscall coverage: unshare, __NR_unshare.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability, procfs. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; kernel configuration, procfs visibility, or privileges can change availability; time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/unshare.c -->
