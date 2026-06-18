<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/strace--decode-pids-comm.c -->
# sources/test-tools/strace/tests/strace--decode-pids-comm.c

## Purpose
Covers strace command-line option behavior. Source comments/macros state: Test -Y/--decode-pids=comm option. The executable built from this source file should have a long name (> 16) to test how strace reports the initial value of /proc/$pid/comm. Even if linux returns a longer name, strace should not crash. Source read: 123 lines, 3042 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <errno.h>, <signal.h>, <stdio.h>, <stdlib.h>, <string.h>, <sys/prctl.h>, <unistd.h>, <sys/types.h>, <sys/wait.h>; defines/undefs: NEW_NAME; C functions: do_default_action, do_execve_action, main; syscall numbers/wrappers: tgkill, __NR_tgkill.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. loops enumerate flag, pointer, descriptor, pid, or xlat-mode combinations. process/thread branches synchronize children or threads before final trace comparison. primary syscall coverage: tgkill, __NR_tgkill.

## State And Persistence Behavior
owns transient child/thread lifecycle state that must be synchronized before exit.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability, procfs. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; process/thread ordering can make trace matching fragile; kernel configuration, procfs visibility, or privileges can change availability. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/strace--decode-pids-comm.c -->
