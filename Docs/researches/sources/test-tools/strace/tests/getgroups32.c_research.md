<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getgroups32.c -->
# sources/test-tools/strace/tests/getgroups32.c

## Purpose
Covers strace self-test coverage for `getgroups32`. Source read: 19 lines, 273 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", "getgroups.c"; defines: none; syscall names/numbers: getgroups32.

## Control Flow
primary syscall coverage is getgroups32.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability, shared implementation `getgroups.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getgroups32.c -->
