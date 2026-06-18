<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/strace--syscall-limit-status-summary.c -->
# sources/test-tools/strace/tests/strace--syscall-limit-status-summary.c

## Purpose
Variant wrapper for `strace--syscall-limit.c`. It defines `PRINT_VALID, PRINT_STATS, UNLINKAT_CNT, TOTAL_CNT` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 5 lines, 122 bytes.

## Important APIs, Types, And Functions
includes/imports: "strace--syscall-limit.c"; defines/undefs: PRINT_VALID, PRINT_STATS, UNLINKAT_CNT, TOTAL_CNT.

## Control Flow
Preprocessor-only flow: set `PRINT_VALID, PRINT_STATS, UNLINKAT_CNT, TOTAL_CNT`, include `strace--syscall-limit.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on shared implementation `strace--syscall-limit.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/strace--syscall-limit-status-summary.c -->
