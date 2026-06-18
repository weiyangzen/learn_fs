<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/threads-execve.c -->
# sources/test-tools/strace/tests/threads-execve.c

## Purpose
Covers threaded execve tracing and quietness modes. Source comments/macros state: Check decoding of threads when a non-leader thread invokes execve. %u vars %u vars %u vars %u vars Source read: 245 lines, 5742 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <errno.h>, <pthread.h>, <signal.h>, <stdio.h>, <stdlib.h>, <time.h>, <unistd.h>, "kernel_old_timespec.h"; defines/undefs: PRINT_EXITED, PRINT_SUPERSEDED; C functions: handler, k_sigsuspend, k_gettid, get_sigsetsize, arglen, main; syscall numbers/wrappers: nanosleep, rt_sigsuspend, gettid, clock_nanosleep, exit, __NR_rt_sigsuspend, __NR_gettid, __NR_clock_nanosleep, __NR_nanosleep, __NR_exit; struct types: sigaction.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. loops enumerate flag, pointer, descriptor, pid, or xlat-mode combinations. process/thread branches synchronize children or threads before final trace comparison. temporary kernel objects are created to exercise descriptor, timer, or socket decoding. primary syscall coverage: nanosleep, rt_sigsuspend, gettid, clock_nanosleep, exit, __NR_rt_sigsuspend, __NR_gettid, __NR_clock_nanosleep, __NR_nanosleep, __NR_exit.

## State And Persistence Behavior
owns transient child/thread lifecycle state that must be synchronized before exit.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability, pthread support. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; process/thread ordering can make trace matching fragile; time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/threads-execve.c -->
