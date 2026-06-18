<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/waitpid.c -->
# sources/test-tools/strace/tests/waitpid.c

## Purpose
Covers strace decoder coverage for `waitpid`. Source comments/macros state: Check decoding of waitpid syscall. Source read: 36 lines, 691 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>, <sys/wait.h>; defines/undefs: none; C functions: main; syscall numbers/wrappers: waitpid, __NR_waitpid.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. process/thread branches synchronize children or threads before final trace comparison. primary syscall coverage: waitpid, __NR_waitpid.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/waitpid.c -->
