<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fstatfs64.c -->
# sources/test-tools/strace/tests/fstatfs64.c

## Purpose
Covers strace self-test coverage for `fstatfs64`. Source read: 24 lines, 472 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", "xstatfs64.c"; defines: SYSCALL_ARG_FMT, SYSCALL_ARG, SYSCALL_NR, SYSCALL_NAME; syscall names/numbers: fstatfs64.

## Control Flow
primary syscall coverage is fstatfs64.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability, shared implementation `xstatfs64.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fstatfs64.c -->
