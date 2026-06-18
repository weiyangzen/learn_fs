<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/umoven-illptr.c -->
# sources/test-tools/strace/tests/umoven-illptr.c

## Purpose
Covers strace decoder coverage for `umoven-illptr`. Source comments/macros state: Check decoding of invalid pointer by umoven. Source read: 57 lines, 1181 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <unistd.h>, "kernel_old_timespec.h"; defines/undefs: none; C functions: k_nanosleep, main; syscall numbers/wrappers: nanosleep, __NR_nanosleep.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: nanosleep, __NR_nanosleep.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/umoven-illptr.c -->
