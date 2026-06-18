<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fstatat.c -->
# sources/test-tools/strace/tests/fstatat.c

## Purpose
Covers strace self-test coverage for `fstatat`. Source read: 28 lines, 668 bytes.

## Important APIs, Types, And Functions
includes/imports: "xstatx.c"; defines: TEST_SYSCALL_INVOKE, PRINT_SYSCALL_HEADER, PRINT_SYSCALL_FOOTER; syscall names/numbers: TEST_SYSCALL_NR.

## Control Flow
primary syscall coverage is TEST_SYSCALL_NR.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on shared implementation `xstatx.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared; skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fstatat.c -->
