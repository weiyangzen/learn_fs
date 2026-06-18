<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/waitid-v.c -->
# sources/test-tools/strace/tests/waitid-v.c

## Purpose
Variant wrapper for `waitid.c`. It defines `VERBOSE` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 3 lines, 87 bytes.

## Important APIs, Types, And Functions
includes/imports: "waitid.c"; defines/undefs: VERBOSE.

## Control Flow
Preprocessor-only flow: set `VERBOSE`, include `waitid.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on shared implementation `waitid.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: process/thread ordering can make trace matching fragile. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/waitid-v.c -->
