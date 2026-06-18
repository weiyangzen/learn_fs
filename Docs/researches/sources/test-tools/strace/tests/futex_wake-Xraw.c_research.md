<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/futex_wake-Xraw.c -->
# sources/test-tools/strace/tests/futex_wake-Xraw.c

## Purpose
Variant wrapper that includes `futex_wake.c` after defining `XLAT_RAW`. It lets the same compiled test exercise a different strace output mode without duplicating the base implementation. Source read: 2 lines, 43 bytes.

## Important APIs, Types, And Functions
includes/imports: "futex_wake.c"; defines: XLAT_RAW.

## Control Flow
Preprocessor control flow only: define `XLAT_RAW`, include `futex_wake.c`, and inherit that file's `main` and helper functions.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on shared implementation `futex_wake.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: expected output depends on xlat raw/abbrev/verbose formatting. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/futex_wake-Xraw.c -->
