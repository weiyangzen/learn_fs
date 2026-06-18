<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/times-Xraw.c -->
# sources/test-tools/strace/tests/times-Xraw.c

## Purpose
Variant wrapper for `times.c`. It defines `XLAT_RAW` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 2 lines, 38 bytes.

## Important APIs, Types, And Functions
includes/imports: "times.c"; defines/undefs: XLAT_RAW.

## Control Flow
Preprocessor-only flow: set `XLAT_RAW`, include `times.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on shared implementation `times.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: expected output is sensitive to xlat and string-escaping mode; time formatting and clock/timer state require tolerance for kernel and libc differences. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/times-Xraw.c -->
