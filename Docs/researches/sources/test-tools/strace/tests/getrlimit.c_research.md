<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getrlimit.c -->
# sources/test-tools/strace/tests/getrlimit.c

## Purpose
Covers strace self-test coverage for `getrlimit`. Source read: 21 lines, 342 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", "xgetrlimit.c"; defines: NR_GETRLIMIT, STR_GETRLIMIT; syscall names/numbers: getrlimit.

## Control Flow
primary syscall coverage is getrlimit.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability, shared implementation `xgetrlimit.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getrlimit.c -->
