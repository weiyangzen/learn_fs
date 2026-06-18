<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/wait4.c -->
# sources/test-tools/strace/tests/wait4.c

## Purpose
Covers strace decoder coverage for `wait4`. Source comments/macros state: Check decoding of wait4 syscall. WCONTINUED && WIFCONTINUED __NR_wait4 Source read: 207 lines, 5371 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <assert.h>, <signal.h>, <stdio.h>, <unistd.h>, <sys/wait.h>, "kernel_rusage.h"; defines/undefs: none; C functions: sprint_rusage, k_wait4, do_wait4, main; syscall numbers/wrappers: wait4, __NR_wait4.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. process/thread branches synchronize children or threads before final trace comparison. temporary kernel objects are created to exercise descriptor, timer, or socket decoding. primary syscall coverage: wait4, __NR_wait4.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries; owns transient child/thread lifecycle state that must be synchronized before exit.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; process/thread ordering can make trace matching fragile; time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/wait4.c -->
