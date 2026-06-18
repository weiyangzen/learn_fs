<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/tkill--pidns-translation.c -->
# sources/test-tools/strace/tests/tkill--pidns-translation.c

## Purpose
Variant wrapper for `tkill.c`. It defines `PIDNS_TRANSLATION` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 2 lines, 45 bytes.

## Important APIs, Types, And Functions
includes/imports: "tkill.c"; defines/undefs: PIDNS_TRANSLATION.

## Control Flow
Preprocessor-only flow: set `PIDNS_TRANSLATION`, include `tkill.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on shared implementation `tkill.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: pid namespace translation depends on namespace support and synchronization. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/tkill--pidns-translation.c -->
