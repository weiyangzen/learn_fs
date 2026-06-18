<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fork--pidns-translation.c -->
# sources/test-tools/strace/tests/fork--pidns-translation.c

## Purpose
Covers strace self-test coverage for `fork--pidns-translation`. Source comments describe: Test PID namespace translation Source read: 75 lines, 1202 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", "pidns.h", <errno.h>, <limits.h>, <sched.h>, <signal.h>, <stdio.h>, <stdlib.h>, <sys/wait.h>, <unistd.h>, <linux/sched.h>, <linux/nsfs.h>; defines: none; C functions: fork_chain, main; syscall names/numbers: fork, __NR_fork.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. process/thread branches use `fork`, `pthread`, pipes, or wait helpers to produce traceable lifecycle events. primary syscall coverage is fork, __NR_fork.

## State And Persistence Behavior
child processes or threads are synchronized and reaped before test exit.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, `pidns.h`, Linux UAPI headers, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling; pid namespace translation is sensitive to namespace support and parent/child synchronization; concurrency and process ordering can make trace matching fragile. Test signals: skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fork--pidns-translation.c -->
