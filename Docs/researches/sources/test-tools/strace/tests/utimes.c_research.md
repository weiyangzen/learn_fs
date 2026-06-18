<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/utimes.c -->
# sources/test-tools/strace/tests/utimes.c

## Purpose
Covers strace decoder coverage for `utimes`. Source comments/macros state: Check decoding of utimes syscall. Source read: 26 lines, 503 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", "kernel_timeval.h", "xutimes.c"; defines/undefs: TEST_SYSCALL_NR, TEST_SYSCALL_STR, TEST_STRUCT; syscall numbers/wrappers: utimes.

## Control Flow
primary syscall coverage: utimes.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, `kernel_timeval.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/utimes.c -->
