<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/xmalloc_for_tests.c -->
# sources/test-tools/strace/tests/xmalloc_for_tests.c

## Purpose
Variant wrapper for `xmalloc.c`. It defines `error_msg_and_die` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 2 lines, 66 bytes.

## Important APIs, Types, And Functions
includes/imports: "xmalloc.c"; defines/undefs: error_msg_and_die.

## Control Flow
Preprocessor-only flow: set `error_msg_and_die`, include `xmalloc.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on shared implementation `xmalloc.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/xmalloc_for_tests.c -->
