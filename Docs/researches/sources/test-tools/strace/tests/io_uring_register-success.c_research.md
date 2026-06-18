<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/io_uring_register-success.c -->
# sources/test-tools/strace/tests/io_uring_register-success.c

## Purpose
Variant wrapper that includes `io_uring_register.c` after defining `RETVAL_INJECTED`. It lets the same compiled test exercise a different strace output mode without duplicating the base implementation. Source read: 2 lines, 57 bytes.

## Important APIs, Types, And Functions
includes/imports: "io_uring_register.c"; defines: RETVAL_INJECTED.

## Control Flow
Preprocessor control flow only: define `RETVAL_INJECTED`, include `io_uring_register.c`, and inherit that file's `main` and helper functions.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on shared implementation `io_uring_register.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/io_uring_register-success.c -->
