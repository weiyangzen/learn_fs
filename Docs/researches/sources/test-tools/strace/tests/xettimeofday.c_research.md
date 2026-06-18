<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/xettimeofday.c -->
# sources/test-tools/strace/tests/xettimeofday.c

## Purpose
Covers strace decoder coverage for `xettimeofday`. Source comments/macros state: __NR_gettimeofday Source read: 77 lines, 2298 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", "kernel_timeval.h", <assert.h>, <stdio.h>, <stdint.h>, <unistd.h>, <sys/time.h>; defines/undefs: none; C functions: main; syscall numbers/wrappers: gettimeofday, settimeofday, __NR_gettimeofday, __NR_settimeofday; struct types: timezone.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: gettimeofday, settimeofday, __NR_gettimeofday, __NR_settimeofday.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, `kernel_timeval.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/xettimeofday.c -->
