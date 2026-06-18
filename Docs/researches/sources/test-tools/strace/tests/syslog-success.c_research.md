<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/syslog-success.c -->
# sources/test-tools/strace/tests/syslog-success.c

## Purpose
Variant wrapper for `syslog.c`. It defines `RETVAL_INJECTED` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 2 lines, 46 bytes.

## Important APIs, Types, And Functions
includes/imports: "syslog.c"; defines/undefs: RETVAL_INJECTED.

## Control Flow
Preprocessor-only flow: set `RETVAL_INJECTED`, include `syslog.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on shared implementation `syslog.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel configuration, procfs visibility, or privileges can change availability. Test signals: successful compilation and strace harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/syslog-success.c -->
