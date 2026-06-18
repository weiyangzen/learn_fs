<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/utime.c -->
# sources/test-tools/strace/tests/utime.c

## Purpose
Covers strace decoder coverage for `utime`. Source comments/macros state: Check decoding of utime syscall. Source read: 66 lines, 1599 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <time.h>, <utime.h>, <errno.h>, <stdio.h>, <unistd.h>; defines/undefs: none; C functions: k_utime, main; syscall numbers/wrappers: utime, __NR_utime; struct types: utimbuf, tm.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: utime, __NR_utime.

## State And Persistence Behavior
observes or mutates time/timer state only inside the test process or temporary file.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/utime.c -->
