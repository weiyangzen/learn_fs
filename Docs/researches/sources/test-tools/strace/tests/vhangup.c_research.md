<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/vhangup.c -->
# sources/test-tools/strace/tests/vhangup.c

## Purpose
Covers strace decoder coverage for `vhangup`. Source comments/macros state: Check decoding of vhangup syscall. On setsid() success, the new session has no controlling terminal, therefore a subsequent vhangup() has nothing to hangup. The system call, however, returns 0 iff the calling process has CAP_SYS_TTY_CONFIG capability. Source read: 35 lines, 691 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>; defines/undefs: none; C functions: main; syscall numbers/wrappers: vhangup, __NR_vhangup.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: vhangup, __NR_vhangup.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/vhangup.c -->
