<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/time.c -->
# sources/test-tools/strace/tests/time.c

## Purpose
Covers strace decoder coverage for `time`. Source comments/macros state: This file is part of time strace test. Source read: 75 lines, 1558 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <errno.h>, <stdio.h>, <stdint.h>, <unistd.h>; defines/undefs: none; C functions: main; syscall numbers/wrappers: time, __NR_time.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: time, __NR_time.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/time.c -->
