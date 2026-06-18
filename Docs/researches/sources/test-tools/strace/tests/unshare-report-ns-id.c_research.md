<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/unshare-report-ns-id.c -->
# sources/test-tools/strace/tests/unshare-report-ns-id.c

## Purpose
Variant wrapper for `unshare.c`. It defines `PRINT_NAMESPACE` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 2 lines, 45 bytes.

## Important APIs, Types, And Functions
includes/imports: "unshare.c"; defines/undefs: PRINT_NAMESPACE.

## Control Flow
Preprocessor-only flow: set `PRINT_NAMESPACE`, include `unshare.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on shared implementation `unshare.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/unshare-report-ns-id.c -->
