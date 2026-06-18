<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/status-detached-threads.c -->
# sources/test-tools/strace/tests/status-detached-threads.c

## Purpose
Covers strace status filtering and status-summary behavior. Source comments/macros state: Check status=detached filtering when a non-leader thread invokes execve. Source read: 56 lines, 1205 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <errno.h>, <pthread.h>, <stdio.h>, <time.h>, <unistd.h>; defines/undefs: none; C functions: main; syscall numbers/wrappers: gettid, __NR_gettid; struct types: timespec.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. process/thread branches synchronize children or threads before final trace comparison. primary syscall coverage: gettid, __NR_gettid.

## State And Persistence Behavior
owns transient child/thread lifecycle state that must be synchronized before exit.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability, pthread support. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; process/thread ordering can make trace matching fragile; time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: stdout emits canonical expected trace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/status-detached-threads.c -->
