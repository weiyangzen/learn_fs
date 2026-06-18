<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/waitid.c -->
# sources/test-tools/strace/tests/waitid.c

## Purpose
Covers strace decoder coverage for `waitid`. Source comments/macros state: Check decoding of waitid syscall. WCONTINUED Source read: 274 lines, 6552 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <assert.h>, <signal.h>, <stdio.h>, <string.h>, <unistd.h>, <sys/wait.h>, "kernel_rusage.h", "scno.h"; defines/undefs: MY_COMM, SKIP_IF_PROC_IS_UNAVAILABLE, CASE; C functions: sprint_rusage, si_code_2_name, sprint_siginfo, poison, do_waitid, main; syscall numbers/wrappers: waitid, __NR_waitid.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. process/thread branches synchronize children or threads before final trace comparison. temporary kernel objects are created to exercise descriptor, timer, or socket decoding. primary syscall coverage: waitid, __NR_waitid.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries; owns transient child/thread lifecycle state that must be synchronized before exit.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; process/thread ordering can make trace matching fragile; time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/waitid.c -->
