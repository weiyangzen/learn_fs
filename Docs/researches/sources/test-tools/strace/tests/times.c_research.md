<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/times.c -->
# sources/test-tools/strace/tests/times.c

## Purpose
Covers strace decoder coverage for `times`. Source comments/macros state: Check decoding of times syscall. @file This test burns some CPU cycles in user space and kernel space in order to get some non-zero values returned by times(2). On systems where user's and kernel's long types are the same, prefer direct times syscall over libc's times function because the latter is more prone to return value truncation. %.*f s %.*f s %.*f s %.*f s Source read: 128 lines, 3180 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <fcntl.h>, <sched.h>, <stdio.h>, <time.h>, <unistd.h>, "scno.h", <sys/stat.h>, <sys/times.h>, <sys/types.h>, <sys/wait.h>, "time_enjoyment.h"; defines/undefs: none; C functions: main; syscall numbers/wrappers: times, __NR_times; struct types: tms.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. process/thread branches synchronize children or threads before final trace comparison. primary syscall coverage: times, __NR_times.

## State And Persistence Behavior
owns transient child/thread lifecycle state that must be synchronized before exit.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, `time_enjoyment.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; expected output is sensitive to xlat and string-escaping mode; process/thread ordering can make trace matching fragile; time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: stdout emits canonical expected trace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/times.c -->
