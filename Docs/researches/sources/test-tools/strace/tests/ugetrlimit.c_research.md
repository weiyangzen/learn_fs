<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ugetrlimit.c -->
# sources/test-tools/strace/tests/ugetrlimit.c

## Purpose
Covers strace decoder coverage for `ugetrlimit`. Source read: 21 lines, 346 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", "xgetrlimit.c"; defines/undefs: NR_GETRLIMIT, STR_GETRLIMIT; syscall numbers/wrappers: ugetrlimit.

## Control Flow
primary syscall coverage: ugetrlimit.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling. Test signals: unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ugetrlimit.c -->
