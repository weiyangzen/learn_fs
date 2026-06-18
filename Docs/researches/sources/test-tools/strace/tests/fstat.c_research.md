<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fstat.c -->
# sources/test-tools/strace/tests/fstat.c

## Purpose
Covers strace self-test coverage for `fstat`. Source read: 23 lines, 455 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", "fstatx.c"; defines: TEST_SYSCALL_NR, TEST_SYSCALL_STR, SAMPLE_SIZE; syscall names/numbers: fstat.

## Control Flow
primary syscall coverage is fstat.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability, shared implementation `fstatx.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fstat.c -->
