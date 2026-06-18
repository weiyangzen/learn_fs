<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/waitid-Y.c -->
# sources/test-tools/strace/tests/waitid-Y.c

## Purpose
Variant wrapper for `waitid.c`. It defines `MY_COMM, SKIP_IF_PROC_IS_UNAVAILABLE` before inclusion, so the shared implementation is compiled under a specific output, status, pid-translation, or xlat mode without duplicating the base test body. Source read: 3 lines, 123 bytes.

## Important APIs, Types, And Functions
includes/imports: "waitid.c"; defines/undefs: MY_COMM, SKIP_IF_PROC_IS_UNAVAILABLE.

## Control Flow
Preprocessor-only flow: set `MY_COMM, SKIP_IF_PROC_IS_UNAVAILABLE`, include `waitid.c`, and inherit its `main` or script logic.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on procfs, shared implementation `waitid.c`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: process/thread ordering can make trace matching fragile; kernel configuration, procfs visibility, or privileges can change availability. Test signals: unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/waitid-Y.c -->
