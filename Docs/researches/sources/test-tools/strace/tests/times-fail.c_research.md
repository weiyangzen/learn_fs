<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/times-fail.c -->
# sources/test-tools/strace/tests/times-fail.c

## Purpose
Covers strace decoder coverage for `times-fail`. Source read: 22 lines, 368 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <assert.h>, <stdio.h>, <unistd.h>, "scno.h"; defines/undefs: none; C functions: main; syscall numbers/wrappers: times, __NR_times.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: times, __NR_times.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: stdout emits canonical expected trace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/times-fail.c -->
