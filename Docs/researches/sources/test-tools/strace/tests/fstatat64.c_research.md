<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fstatat64.c -->
# sources/test-tools/strace/tests/fstatat64.c

## Purpose
Covers strace self-test coverage for `fstatat64`. Source read: 25 lines, 513 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", "fstatat.c"; defines: TEST_SYSCALL_NR, TEST_SYSCALL_STR, STRUCT_STAT, STRUCT_STAT_STR, STRUCT_STAT_IS_STAT64; syscall names/numbers: fstatat64; struct types: stat64.

## Control Flow
primary syscall coverage is fstatat64.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability, shared implementation `fstatat.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fstatat64.c -->
